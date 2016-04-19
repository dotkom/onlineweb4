# -*- coding: utf-8 -*-

import random
from hashlib import sha256

from django.conf import settings
from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import ugettext as _

User = settings.AUTH_USER_MODEL

# Statics

QUESTION_TYPES = [
    (0, _('Ja/Nei')),
    (1, _('Multiple Choice')),
]

MAJORITY_TYPES = [
    (0, _('Alminnelig flertall (1/2)')),
    (1, _('Kvalifisert flertall (2/3)')),
]

BOOLEAN_VOTE = 0
MULTIPLE_CHOICE = 1

# General genfors model


class Meeting(models.Model):
    """
    The Meeting model encapsulates a single Generalforsamling with all cascading one-to-many relationships
    """

    start_date = models.DateTimeField(_('Tidspunkt'), help_text=_('Tidspunkt for arrangementsstart'), null=False)
    title = models.CharField(_('Tittel'), max_length=150, null=False)
    registration_locked = models.BooleanField(
        _('registration_lock'),
        help_text=_('Steng registrering'),
        default=True,
        blank=False,
        null=False
    )
    ended = models.BooleanField(
        _('event_lockdown'),
        help_text=_('Avslutt generalforsamlingen'),
        default=False,
        blank=False,
        null=False
    )
    pin = models.CharField(_('Pinkode'), max_length=8, null=False, default='stub')

    def __str__(self):
        return self.title + ' (' + localtime(self.start_date).strftime("%d/%m/%y %H:%M") + ')'

    def get_pin_code(self):
        return self.pin

    # Pincode generator for a particular meeting
    def generate_pin_code(self):
        h = sha256()
        h.update(str(random.randint(0, 100000)).encode('utf-8'))
        h = h.hexdigest()
        self.pin = h[:6]
        self.save()

    # Return the number of attendees
    def num_attendees(self):
        return RegisteredVoter.objects.filter(meeting=self).count()

    # Returns the number of registered voter that are eligible to vote at the time of calling the function
    def num_can_vote(self):
        return RegisteredVoter.objects.filter(meeting=self, can_vote=True).count()

    # Returns the result set of registered voter objects that can vote at the time of calling the function
    def get_can_vote(self):
        return RegisteredVoter.objects.filter(meeting=self, can_vote=True)

    # Get attendee list as a list of strings
    def get_attendee_list(self):
        return RegisteredVoter.objects.filter(meeting=self).order_by('user__first_name', 'user__last_name')

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
    @staticmethod
    def get_results_from_question(question):
        return question.get_results()

    class Meta(object):
        verbose_name = _('Generalforsamling')
        verbose_name_plural = _('Generalforsamlinger')
        permissions = (
            ('view_meeting', 'View Meeting'),
        )


# USER RELATED MODELS


class AbstractVoter(models.Model):
    meeting = models.ForeignKey(Meeting, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('view_abstractvoter', 'View AbstractVoter'),
        )


class RegisteredVoter(AbstractVoter):
    """
    The RegisteredVoter model is a wrapper for OnlineUser with added fields for attendance registry
    porpuses, as well as an added can_vote field for future use.
    """

    user = models.ForeignKey(User, null=False)
    can_vote = models.BooleanField(_('voting_right'), help_text=_('Har stemmerett'), null=False, default=False)

    def __str__(self):
        return self.user.get_full_name()

    class Meta(object):
        permissions = (
            ('view_registeredvoter', 'View RegisteredVoter'),
        )


class AnonymousVoter(AbstractVoter):
    """
    AnonymousVoter model is used for anonymous votes and should not be linked with a user model
    The hash is calculated from SECRET_KEY, username and a salt provided by the user (which is never stored)
    """

    # sha256
    user_hash = models.CharField(null=False, max_length=64)

    def __str__(self):
        return self.user_hash[:12]

    class Meta(object):
        permissions = (
            ('view_anonymousvoter', 'View AnonymousVoter'),
        )


# Question wrapper


class Question(models.Model):
    """
    A question is a wrapper to which all votes must be connected.
    """

    meeting = models.ForeignKey(Meeting, help_text=_('Generalforsamling'), null=False)
    anonymous = models.BooleanField(_('Hemmelig valg'), default=False, null=False, blank=False)
    created_time = models.DateTimeField(_('added'), auto_now_add=True)
    locked = models.BooleanField(
        _('locked'),
        help_text=_('Steng avstemmingen'),
        null=False,
        blank=False,
        default=False
    )
    question_type = models.SmallIntegerField(
        _('Spørsmålstype'),
        choices=QUESTION_TYPES,
        default=0,
    )
    description = models.TextField(
        _('Beskrivelse'),
        help_text=_('Beskrivelse av saken som skal stemmes over'),
        max_length=500,
        blank=True
    )
    majority_type = models.SmallIntegerField(
        _('Flertallstype'),
        choices=MAJORITY_TYPES,
        default=0,
    )
    only_show_winner = models.BooleanField(_('Vis kun vinner'), null=False, blank=False, default=False)
    total_voters = models.IntegerField(_('Stemmeberettigede'), null=True)
    count_blank_votes = models.BooleanField(_('Tellende blanke stemmer'), null=False, blank=False, default=False)

    # Returns results as a dictionary, either by alternative or boolean-ish types
    def get_results(self, admin=False):
        from apps.genfors.utils import get_results  # noqa - need to import here to prevent circular importing
        return get_results(self, admin)

    def get_admin_results(self):
        return self.get_results(admin=True)

    # Gets the name of the alt with the most votes
    def get_leader(self):
        results = self.get_results()
        if results and self.count_blank_votes:
            return max(results['data'].keys(), key=lambda key: results['data'][key])
        elif results and not self.count_blank_votes:
            if 'Blankt' in results['data']:
                results['data'].pop('Blankt', None)
            try:
                return max(results['data'].keys(), key=lambda key: results['data'][key])
            except ValueError:
                return None
        else:
            return None

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

    def __str__(self):
        return '[%d] %s' % (self.id - self.meeting.num_questions(), self.description)

    class Meta:
        permissions = (
            ('view_question', 'View Question'),
        )


# Individual abstract vote and vote types


class AbstractVote(models.Model):
    """
    The AbstractVote model holds some key components of a vote to a specific question
    """

    time = models.DateTimeField(_('timestamp'), auto_now_add=True)
    voter = models.ForeignKey(AbstractVoter, help_text=_('Bruker'), null=False)
    question = models.ForeignKey(Question, null=False)

    def get_voter_name(self):
        return str(self.voter)

    class Meta(object):
        permissions = (
            ('view_abstractvote', 'View AbstractVote'),
        )


class BooleanVote(AbstractVote):
    """
    The BooleanVote model holds the yes/no/blank answer to a specific question held in superclass
    """

    answer = models.NullBooleanField(_('answer'), help_text=_('Ja/Nei'), null=True, blank=True)

    class Meta(object):
        permissions = (
            ('view_booleanvote', 'View BooleanVote'),
        )


class Alternative(models.Model):
    """
    The Alternative class represents a single alternative that
    is connected to a particular multiple choice type question
    """

    alt_id = models.PositiveIntegerField(help_text=_('Alternativ ID'))
    question = models.ForeignKey(Question, null=False, help_text=_('Question'))
    description = models.CharField(_('Beskrivelse'), null=True, blank=True, max_length=150)

    def __str__(self):
        return self.description

    class Meta(object):
        permissions = (
            ('view_alternative', 'View Alternative'),
        )


class MultipleChoice(AbstractVote):
    """
    The MultipleChoice model holds the answered alternative to a specific question held in superclass
    """

    answer = models.ForeignKey(Alternative, null=True, blank=True, help_text=_('Alternativ'))

    class Meta(object):
        permissions = (
            ('view_multiplechoice', 'View MultipleChoice'),
        )


class Result(models.Model):
    """
    Result string container to reduce serverload
    """

    meeting = models.ForeignKey(Meeting, null=False, help_text='Meeting')
    question = models.ForeignKey(Question, null=False, help_text='Meeting')
    result_public = models.TextField(max_length=2000)
    result_private = models.TextField(max_length=2000)

    class Meta(object):
        permissions = (
            ('view_result', 'View Result'),
        )
