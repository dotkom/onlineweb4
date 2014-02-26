from datetime import datetime
from django.db import models
from apps.authentication.models import OnlineUser as User
from django.utils.translation import ugettext as _
from hashlib import sha256
from django.conf import settings

# Statics

QUESTION_TYPES = [
    (0, _(u'Ja/Nei')),
    (1, _(u'Multiple Choice')),
]

# General genfors model

class Meeting(models.Model):
    '''
    The Meeting model encapsulates a single Generalforsamling with all cascading one-to-many relationships
    '''
    start_date = models.DateTimeField(_(u'date'), help_text=_('Dato for arrangementsstart'), null=False)
    title = models.CharField(_(u'title'), max_length=150, null=False)
    registration_locked = models.BooleanField(_(u'registration_lock'), help_text=_(u'Steng registrering'), default=False, blank=False, null=False)
    ended = models.BooleanField(_(u'event_lockdown'), help_text=_(u'Avslutt generalforsamlingen'), default=False, blank=False, null=False)

    def __unicode__(self):
        return self.title + ' (' + self.start_date.ctime() + ')'

    def num_attendees(self):
        return RegisteredVoter.objects.filter(meeting=self).count()

    def get_attendee_list(self):
        return sorted([u'%s, %s' %(a.user.last_name, a.user.first_name) for a in RegisteredVoter.objects.filter(meeting=self)])

    def get_questions(self):
        return Question.objects.filter(meeting=self).order_by('-id')

    def get_active_question(self):
        question = self.get_questions()
        if question and not question[0].locked:
            return question[0]
        else:
            return None

    def get_locked_questions(self):
        return self.get_questions().filter(locked=True)

    def num_questions(self):
        return Question.objects.filter(meeting=self).count()

    def get_results_from_question(self, question):
        return question.get_results()

    class Meta:
        verbose_name = _(u'Generalforsamling')
        verbose_name_plural = _(u'Generalforsamlinger')

# User related models

class RegisteredVoter(models.Model):
    '''
    The RegisteredVoter model is a wrapper for OnlineUser with added fields for attendance registry
    porpuses, as well as an added can_vote field for future use.
    '''
    meeting = models.ForeignKey(Meeting, null=False)
    user = models.ForeignKey(User, null=False)
    can_vote = models.BooleanField(_(u'voting_right'), help_text=_(u'Har stemmerett'), null=False, default=True)

    def __unicode__(self):
        return u'%s, %s' %(self.user.last_name, self.user.first_name)

# Question wrapper

class Question(models.Model):
    '''
    A question is a wrapper to which all votes must be connected.
    '''
    meeting = models.ForeignKey(Meeting, help_text=_(u'Generalforsamling'), null=False)
    anonymous = models.BooleanField(_(u'anonymous'), help_text=_(u'Hemmelig valg'), null=False, blank=False)
    created_time = models.DateTimeField(_(u'added'), auto_now_add=True)
    number_of_alternatives = models.PositiveIntegerField(_(u'Antall alternativer'), null=True, blank=True)
    locked = models.BooleanField(_(u'locked'), help_text=_(u'Steng avstemmingen'), null=False, blank=False, default=False)
    question_type = models.SmallIntegerField(_(u'question_type'), help_text=_(u'Type'), choices=QUESTION_TYPES, null=False, default=0)
    description = models.TextField(_(u'description'), help_text=_(u'Beskrivelse av saken som skal stemmes over'), max_length=300, blank=True)
    result = models.CharField(_(u'result'), max_length=100, help_text=_(u'Resultatet av avstemmingen'), null=True, blank=True)

    # Returns results as a dictionary, either by alternative or boolean-ish types
    def get_results(self):
        retults = None

        if self.question_type == 0:
            results = {'JA': 0, 'NEI': 0, 'BLANKT': 0}
            for a in BooleanVote.objects.filter(question=self):
                if a.answer == None:
                    results['BLANKT'] += 1
                elif a.answer == False:
                    results['NEI'] += 1
                elif a.answer == True:
                    results['JA'] += 1
        
        elif self.question_type == 1:
            results = []
            for a in MultipleChoice.objects.filter(question=self):
                alt = a.answer
                if not alt:
                    alt = 0
                results[alt] += 1
                
        return results

    # Resets the question if there has not been enough difference to settle the case
    def reset_question(self):
        BooleanVote.objects.filter(question=self).delete()
        MultipleChoice.objects.filter(question=self).delete()

    # Sets final result as a string for later fast lookup and locks question
    def set_result_and_lock(self):
        r = self.get_results()
        if self.question_type == 0:
            self.result = 'J:' + str(r['JA']) + ' N:' + str(r['NEI']) + ' B:' + str(r['BLANKT'])
        else:
            result_string = ''
            for k in r:
                result_string += str(k) + ':' + str(r[k]) + ' '
            self.result = result_string
        self.locked = True
        self.save()

    # Returns all votes connected to this question
    def get_votes(self):
        if self.question_type == 0:
            return BooleanVote.objects.filter(question=self)
        elif self.question_type == 1:
            return MultipleChoice.objects.filter(question=self)

    def __unicode__(self):
        return u'[%d] %s' %(self.id - self.meeting.num_questions(), self.description)

# Individual abstract vote and vote types

class AbstractVote(models.Model):
    '''
    The AbstractVote model holds some key components of a vote to a specific question
    '''
    time = models.DateTimeField(_(u'timestamp'), auto_now_add=True)
    voter = models.ForeignKey(RegisteredVoter, help_text=_(u'Bruker'), null=False)
    question = models.ForeignKey(Question, null=False)

    # Get voter name
    def get_voter_name(self):
        realname = u'' + self.voter.user.first_name + ' ' + self.voter.user.last_name
        if self.question.anonymous:
            return self.hide_user(realname)
        else:
            return realname

    # Simple hashing function to hide realnames
    def hide_user(self, arg):
        h = sha256()
        h.update(arg)
        h.update(settings.GENFORS_ANON_SALT)
        h = h.hexdigest()[:8]
        return h

class BooleanVote(AbstractVote):
    '''
    The BooleanVote model holds the yes/no/blank answer to a specific question held in superclass
    '''
    answer = models.NullBooleanField(_(u'answer'), help_text=_(u'Ja/Nei'), null=True, blank=True)

    def __unicode__(self):
        realname = u'%s, %s' %(super(BooleanVote, self).voter.user.last_name, super(BooleanVote, self).voter.user.first_name)
        if super(BooleanVote, self).question.anonymous:
            realname = super(BooleanVote, self).hide_user(realname)
        if self.answer is None:
            a = u'blankt'
        elif self.answer:
            a = u'ja'
        else:
            a = u'nei'
        
        return '%s stemte %s ved %s' %(realname, a, super(BooleanVote, self).question)

class MultipleChoice(AbstractVote):
    '''
    The MultipleChoice model holds the answered alternative to a specific question held in superclass
    '''
    answer = models.PositiveIntegerField(null=True, blank=True, help_text=_(u'Alternativ'))

    def __unicode__(self):
        realname = u'%s, %s' %(super(MultipleChoice, self).voter.user.last_name, super(MultipleChoice, self).voter.user.first_name)
        if super(MultipleChoice, self).anonymous:
            realname = super(MultipleChoice, self).hide_user(realname)
        
        return '%s stemte %d ved %s' %(realname, self.answer, super(MultipleChoice, self).question)
