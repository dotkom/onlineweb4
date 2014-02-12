from datetime import datetime
import from django.db import models
from apps.authentication.models import OnlineUser as User
from django.utils.translation import ugettext as _

# General genfors model

class Meeting(models.Model):
    '''
    The Meeting model encapsulates a single Generalforsamling with all cascading one-to-many relationships
    '''
    start_date = models.DateTimeField(_(u'date'), help_text=_('Dato for arrangementsstart'), null=False)
    title = models.CharField(_(u'title'), max_length=150, null=False)
    registration_locked = models.BooleanField(_(u'registration_lock'), help_text=_(u'Lås registrering til generalforsamlingen'), default=False, blank=False, null=False)

    def __unicode__(self):
        return self.title + ' (' + self.start_date + ')'

    def num_attendees(self):
        return RegisteredVoter.objects.filter(meeting=self).count()

    def get_attendee_list(self):
        return sorted(['%s, %s' %(a.user.last_name, a.user.first_name) for a in RegisteredVoter.objects.filter(meeting=self)])

    def get_questions(self):
        return [q for q in Question.objects.filter(meeting=self)]

    

    class Meta:
        verbose_name = _('Generalforsamling')
        verbose_name_plural = _('Generalforsamlinger')

# User related models

class RegisteredVoter(models.Model):
    '''
    The RegisteredVoter model is a wrapper for OnlineUser with added fields for attendance registry
    porpuses, as well as an added can_vote field for future use.
    '''
    meeting = models.ForeignKey(Meeting, related_name=_(u'general_meeting'), null=False)
    user = models.ForeignKey(User, related_name=_(u'registered_voter'), null=False)
    can_vote = models.BooleanField(_(u'voting_right'), help_text=_(u'Har stemmerett'), null=False, default=True)

# Single questions

class Question(models.Model):
    '''
    A question is a wrapper to which all votes must be connected.
    '''
    meeting = models.ForeignKey(Meeting, _(u'meeting'), help_text=_(u'Generalforsamling'), null=False)
    anonymous = models.BooleanField(_(u'anonymous'), help_text=_(u'Hemmelig valg'), null=False, blank=False)
    created_time = models.DateTimeField(_(u'added'), auto_now_add=True)
    nuber_of_alternatives = models.PositiveIntegerField(_(u'Antall alternativer'), null=True, blank=True)
    locked = models.BooleanField(_(u'locked'), help_text=_(u'Låsing av spørsmål'), null=False, blank=False, default=False)

# Individual abstract vote and vote types

class AbstractVote(models.Model):
    '''
    The AbstractVote model holds some key components of a vote to a specific question
    '''
    time = models.DateTimeFIeld(_(u'timestamp'), auto_now_add=True)
    voter = models.ForeignKey(RegisteredVoter, related_name=_(u'votes'), help_text=_(u'Bruker'), null=False)
    question = models.ForeignKey(Question, related_name=_(u'votes'), null=False)

class BooleanVote(AbstractVote):
    '''
    The BooleanVote model holds the yes/no/blank answer to a specific question held in superclass
    '''
    answer = models.BooleanField(_(u'answer'), help_text=_(u'Ja/Nei'), null=True, blank=True)

class MultipleChoice(AbstractVote):
    '''
    The MultipleChoice model holds the answered alternative to a specific question held in superclass
    '''
    answer = models.PositiveIntegerField(null=True, blank=True, help_text=_(u'Alternativ'))
