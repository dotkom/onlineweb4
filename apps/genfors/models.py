#-*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from apps.authentication.models import OnlineUser as User
from django.utils.translation import ugettext as _
from hashlib import sha256
from django.conf import settings
import operator

# Statics

QUESTION_TYPES = [
    (0, _(u'Ja/Nei')),
    (1, _(u'Multiple Choice')),
]

BOOLEAN_VOTE = 0
MULTIPLE_CHOICE = 1

# General genfors model


class Meeting(models.Model):
    '''
    The Meeting model encapsulates a single Generalforsamling with all cascading one-to-many relationships
    '''
    start_date = models.DateTimeField(_(u'Dato'), help_text=_('Dato for arrangementsstart'), null=False)
    title = models.CharField(_(u'Tittel'), max_length=150, null=False)
    registration_locked = models.BooleanField(_(u'registration_lock'), help_text=_(u'Steng registrering'), default=True, blank=False, null=False)
    ended = models.BooleanField(_(u'event_lockdown'), help_text=_(u'Avslutt generalforsamlingen'), default=False, blank=False, null=False)

    def __unicode__(self):
        return self.title + ' (' + self.start_date.strftime("%d/%m/%y") + ')'

    # Return the number of attendees
    def num_attendees(self):
        return RegisteredVoter.objects.filter(meeting=self).count()

    # Get attendee list as a list of strings
    def get_attendee_list(self):
        return sorted([unicode(a) for a in RegisteredVoter.objects.filter(meeting=self)])

    # Get the queryset of all questions
    def get_questions(self):
        return Question.objects.filter(meeting=self).order_by('-id')

    # Get active question, if there is one
    def get_active_question(self):
        question = self.get_questions()
        if question and not question[0].locked:
            return question[0]
        else:
            return None

    # Get all previous questions
    def get_locked_questions(self):
        return self.get_questions().filter(locked=True)

    # Get the number of questions
    def num_questions(self):
        return Question.objects.filter(meeting=self).count()

    # Get results from a specific question
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
    can_vote = models.BooleanField(_(u'voting_right'), help_text=_(u'Har stemmerett'), null=False, default=False)

    # Simple hashing function to hide realnames
    def hide_user(self):
        h = sha256()
        h.update(self.user.get_full_name())
        h.update(settings.SECRET_KEY)
        h = h.hexdigest()[:8]
        return h

    def __unicode__(self):
        return self.user.get_full_name()


# Question wrapper


class Question(models.Model):
    '''
    A question is a wrapper to which all votes must be connected.
    '''
    meeting = models.ForeignKey(Meeting, help_text=_(u'Generalforsamling'), null=False)
    anonymous = models.BooleanField(_(u'Hemmelig valg'), null=False, blank=False)
    created_time = models.DateTimeField(_(u'added'), auto_now_add=True)
    locked = models.BooleanField(_(u'locked'), help_text=_(u'Steng avstemmingen'), null=False, blank=False, default=False)
    question_type = models.SmallIntegerField(_(u'Spørsmålstype'), choices=QUESTION_TYPES, null=False, default=0, blank=False)
    description = models.TextField(_(u'Beskrivelse'), help_text=_(u'Beskrivelse av saken som skal stemmes over'), max_length=500, blank=True)
    result = models.CharField(_(u'result'), max_length=100, help_text=_(u'Resultatet av avstemmingen'), null=True, blank=True)
    only_show_winner = models.BooleanField(_(u'Vis kun vinner'), null=False, blank=False, default=False)

    # Returns results as a dictionary, either by alternative or boolean-ish types
    def get_results(self):
        retults = None

        if self.question_type is BOOLEAN_VOTE:
            results = {'JA': 0, 'NEI': 0, 'BLANKT': 0}
            for a in BooleanVote.objects.filter(question=self):
                if a.answer is None:
                    results['BLANKT'] += 1
                elif a.answer is False:
                    results['NEI'] += 1
                elif a.answer is True:
                    results['JA'] += 1

        elif self.question_type is MULTIPLE_CHOICE:
            mc = MultipleChoice.objects.filter(question=self)
            results = {}
            for a in mc:
                if a.answer is not None:
                    if a.answer.description not in results:
                        results[a.answer.description] = 0
                    results[a.answer.description] += 1
                else:
                    if 0 not in results:
                        results['Blankt'] = 0
                    results['Blankt'] += 1

        return results

    # Fetches the winner of a vote
    def get_winner(self):
        results = self.get_results()
        winner = max(results.iterkeys(), key=(lambda key: results[key]))
        results = {winner: results[winner]}

        return results

    # Returns the queryset of alternatives connected to this question if it is a multiple choice question
    def get_alternatives(self):
        if self.question_type is MULTIPLE_CHOICE:
            return Alternative.objects.filter(question=self)
        else:
            return None

    # Resets the question if there has not been enough difference to settle the case
    def reset_question(self):
        BooleanVote.objects.filter(question=self).delete()
        MultipleChoice.objects.filter(question=self).delete()

    # Sets final result as a string for later fast lookup and locks question
    def set_result_and_lock(self):
        r = self.get_results()
        if self.question_type is BOOLEAN_VOTE:
            self.result = 'J:' + str(r['JA']) + ' N:' + str(r['NEI']) + ' B:' + str(r['BLANKT'])
        elif self.question_type is MULTIPLE_CHOICE:
            result_string = ''
            if self.only_show_winner:
                r = self.get_winner()
                for k, v in r.items():
                    result_string += u'%s' % (str(k))
            else:
                for k, v in r.items():
                    result_string += u'%s: %s ' % (str(k), str(v))
            self.result = result_string
        self.locked = True
        self.save()

    # Returns all votes connected to this question
    def get_votes(self):
        if self.question_type is BOOLEAN_VOTE:
            return BooleanVote.objects.filter(question=self)
        elif self.question_type is MULTIPLE_CHOICE:
            return MultipleChoice.objects.filter(question=self)

    # Check if a RegisteredVoter already has voted on this question
    def already_voted(self, v):
        if self.question_type is BOOLEAN_VOTE:
            return BooleanVote.objects.filter(question=self, voter=v).count()
        elif self.question_type is MULTIPLE_CHOICE:
            return MultipleChoice.objects.filter(question=self, voter=v).count()

    def __unicode__(self):
        return u'[%d] %s' % (self.id - self.meeting.num_questions(), self.description)

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
        if self.question.anonymous:
            return voter.hide_user()
        else:
            return self.voter.user.get_full_name()


class BooleanVote(AbstractVote):
    '''
    The BooleanVote model holds the yes/no/blank answer to a specific question held in superclass
    '''
    answer = models.NullBooleanField(_(u'answer'), help_text=_(u'Ja/Nei'), null=True, blank=True)


class Alternative(models.Model):
    '''
    The Alternative class represents a single alternative that is connected to a particular multiple choice type question
    '''
    alt_id = models.PositiveIntegerField(null=False, help_text=_(u'Alternativ ID'), blank=False)
    question = models.ForeignKey(Question, null=False, help_text=_(u'Question'))
    description = models.CharField(_(u'Beskrivelse'), null=True, blank=True, max_length=150)

    def __unicode__(self):
        return self.description


class MultipleChoice(AbstractVote):
    '''
    The MultipleChoice model holds the answered alternative to a specific question held in superclass
    '''
    answer = models.ForeignKey(Alternative, null=True, blank=True, help_text=_(u'Alternativ'))
