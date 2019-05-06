# -*- coding: utf-8 -*-
"""
An anonymous customizable Feedback Schema application.

An Object is connected to a customizable Feedback through FeedbackRelation,
A Feedback can have many Questions.
An Answer is related to an Object and a Question.

This implementation is not very database friendly however, as it does
very many database lookups.
"""
import logging
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, models
from django.urls import reverse
from django.utils.translation import ugettext as _

from apps.authentication.models import FIELD_OF_STUDY_CHOICES

User = settings.AUTH_USER_MODEL


class FeedbackRelation(models.Model):
    """
    A many to many relation between a Generic Object and a Feedback schema.
    """
    feedback = models.ForeignKey('Feedback', verbose_name=_('Tilbakemeldingskjema'), on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    deadline = models.DateField(_('Tidsfrist'))
    gives_mark = models.BooleanField(_('Gir Prikk'), default=True, help_text=_(
        'Gir automatisk prikk til brukere som ikke har svart innen fristen'
    ))
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    first_mail_sent = models.BooleanField(default=False)

    # Keep a record of who has answered. (not /what/ they have answered)
    answered = models.ManyToManyField(
        User,
        related_name='feedbacks',
        blank=True)

    class Meta(object):
        unique_together = ('feedback', 'content_type', 'object_id')

        permissions = (
            ('view_feedbackrelation', 'View FeedbackRelation'),
        )
        default_permissions = ('add', 'change', 'delete')

        verbose_name = _('tilbakemelding')
        verbose_name_plural = _('tilbakemeldinger')

    @property
    def questions(self):
        return self.feedback.questions

    @property
    def ratingquestion(self):
        return self.feedback.ratingquestions

    @property
    def multiple_choice_question(self):
        return self.feedback.multiple_choice_question

    @property
    def description(self):
        if self.content_title():
            return _("Tilbakemelding: " + self.content_title())
        return self.feedback.description

    @property
    def answers(self):
        """
        All answers related to this FeedbackRelation.
        It's a property of the FeedbackRelation, so that when we know
        the Feedback schema and the Object, we can easily get all the
        answers.

        NB!: When creating more Question types, add their answers here
        """
        answers = []
        answers.extend(self.field_of_study_answers.all())
        answers.extend(self.text_answers.all())
        answers.extend(self.rating_answers.all())
        answers.extend(self.multiple_choice_answers.all())
        return sorted(answers, key=lambda x: x.order)  # sort by order

    def answers_to_question(self, question):
        return question.answer.filter(feedback_relation=self)

    def __str__(self):
        return str(self.feedback_id) + ': ' + str(self.content_object)

    def get_absolute_url(self):
        """
        Returns the absolute URL to its `views.feedback`
        """
        return reverse("feedback",
                       args=[self.content_type.app_label,
                             self.content_type.model,
                             self.object_id,
                             self.feedback.feedback_id])

    def can_answer(self, user):
        if user in self.answered.all():
            return False

        if hasattr(self.content_object, "feedback_users"):
            if self.content_object.feedback_users():
                if user not in self.content_object.feedback_users():
                    return False
            else:
                return False
        return True

    def answer_error_message(self, user):
        if user in self.answered.all():
            return _('Du har allerede svart på skjemaet.')

        if hasattr(self.content_object, "feedback_users"):
            if self.content_object.feedback_users():
                if user not in self.content_object.feedback_users():
                    return _('Du har ikke tilgang til å svare på dette skjemaet.')
            else:
                return _('Skjemaet har ingen brukere som kan svare på skjemaet.')

        return _('Ukjent feil.')

    def not_answered(self):
        if hasattr(self.content_object, "feedback_users"):
            return set(self.content_object.feedback_users()).difference(set(self.answered.all()))
        else:
            return False

    def content_email(self):
        if hasattr(self.content_object, "feedback_mail"):
            return self.content_object.feedback_mail()
        else:
            return "missing mail"

    def content_title(self):
        if hasattr(self.content_object, "feedback_title"):
            return self.content_object.feedback_title()
        else:
            return "Missing title"

    def content_end_date(self):
        if hasattr(self.content_object, "feedback_date"):
            return self.content_object.feedback_date()
        else:
            return False

    def content_info(self):
        if hasattr(self.content_object, "feedback_info"):
            return self.content_object.feedback_info()
        else:
            return dict()

    def save(self, *args, **kwargs):
        log = logging.getLogger(__name__)
        new_fbr = not self.pk
        super(FeedbackRelation, self).save(*args, **kwargs)
        if new_fbr:
            token = uuid.uuid4().hex
            try:
                rt = RegisterToken(fbr=self, token=token)
                rt.save()
                log.info('Successfully registered token for fbr %s with token %s' % (self, token))
            except IntegrityError:
                log.error('Failed to register token for fbr %s with token %s' % (self, token))


class Feedback(models.Model):
    """
    A customizable Feedback schema.
    """
    feedback_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(_('beskrivelse'), max_length=100)
    display_field_of_study = models.BooleanField(
        _('Vis studieoversikt'),
        default=True,
        help_text=_('Grafen over studiefelt vil bli vist til bedriften')
    )
    display_info = models.BooleanField(
        _('Vis extra informasjon'),
        default=True,
        help_text=_('En boks med ekstra informasjon vil bli vist til bedriften')
    )
    available = models.BooleanField(
        _('Vis feedbackskjemaet'),
        default=True,
        help_text=_('Dette brukes til å skjule ubrukte skjemaer, lager du et nytt, så ignorer denne.'))

    @property
    def ratingquestions(self):
        rating_question = []
        rating_question.extend(self.rating_questions.all())
        return rating_question

    @property
    def multiple_choice_question(self):
        multiple_choice_question = []
        multiple_choice_question.extend(self.multiple_choice_questions.all())
        return multiple_choice_question

    @property
    def questions(self):
        """
        All questions related to this Feedback schema.
        All the different question types are grouped together in this
        property to easily get all the questions related to this
        Feedback schema.

        NB!: When creating more Question types, add them here.
        """
        questions = []
        questions.extend(self.text_questions.all())
        questions.extend(self.rating_questions.all())
        questions.extend(self.multiple_choice_questions.all())
        return sorted(questions, key=lambda x: x.order)  # sort by order

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = _('tilbakemeldingsskjema')
        verbose_name_plural = _('tilbakemeldingsskjemaer')
        permissions = (
            ('view_feedback', 'View Feedback'),
        )
        default_permissions = ('add', 'change', 'delete')


class FieldOfStudyAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="field_of_study_answers",
        on_delete=models.CASCADE
    )
    answer = models.SmallIntegerField(
        _('Studieretning'), choices=FIELD_OF_STUDY_CHOICES)

    def __str__(self):
        return self.get_answer_display()

    class Meta(object):
        permissions = (
            ('view_fieldofstudyanswer', 'View FieldOfStudyAnswer'),
        )
        default_permissions = ('add', 'change', 'delete')


class TextQuestion(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        related_name='text_questions',
        on_delete=models.CASCADE
    )
    order = models.SmallIntegerField(_('Rekkefølge'), default=10)
    label = models.CharField(_('Spørsmål'), blank=False, max_length=256)
    display = models.BooleanField(_('Vis til bedrift'), default=True)

    def __str__(self):
        return self.label

    class Meta(object):
        permissions = (
            ('view_textquestion', 'View TextQuestion'),
        )
        default_permissions = ('add', 'change', 'delete')


class TextAnswer(models.Model):
    question = models.ForeignKey(
        TextQuestion,
        related_name='answer',
        on_delete=models.CASCADE
    )

    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="text_answers",
        on_delete=models.CASCADE
    )

    answer = models.TextField(_('svar'))

    def __str__(self):
        return self.answer

    @property
    def order(self):
        return self.question.order

    class Meta(object):
        permissions = (
            ('view_textanswer', 'View TextAnswer'),
        )
        default_permissions = ('add', 'change', 'delete')


RATING_CHOICES = [(k, str(k)) for k in range(1, 7)]  # 1 to 6
RATING_CHOICES.insert(0, ("", ""))  # Adds a blank field to prevent 1 from beeing selected by default


class RatingQuestion(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        related_name='rating_questions',
        on_delete=models.CASCADE
    )

    order = models.SmallIntegerField(_('Rekkefølge'), default=20)
    label = models.CharField(_('Spørsmål'), blank=False, max_length=256)
    display = models.BooleanField(_('Vis til bedrift'), default=True)

    def __str__(self):
        return self.label

    class Meta(object):
        permissions = (
            ('view_ratingquestion', 'View RatingQuestion'),
        )
        default_permissions = ('add', 'change', 'delete')


class RatingAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="rating_answers",
        on_delete=models.CASCADE
    )
    answer = models.SmallIntegerField(
        _('karakter'),
        choices=RATING_CHOICES,
        default=0)

    question = models.ForeignKey(
        RatingQuestion,
        related_name='answer',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.get_answer_display()

    @property
    def order(self):
        return self.question.order

    class Meta(object):
        permissions = (
            ('view_ratinganswer', 'View RatingAnswer'),
        )
        default_permissions = ('add', 'change', 'delete')


class MultipleChoiceQuestion(models.Model):
    label = models.CharField(_('Spørsmål'), blank=False, max_length=256)

    class Meta(object):
        verbose_name = _('Flervalgspørsmål')
        verbose_name_plural = _('Flervalgspørsmål')
        permissions = (
            ('view_multiplechoicequestion', 'View MultipleChoiceQuestion'),
        )

    def __str__(self):
        return self.label


class MultipleChoiceRelation(models.Model):
    multiple_choice_relation = models.ForeignKey(
        MultipleChoiceQuestion,
        on_delete=models.CASCADE
    )
    order = models.SmallIntegerField(_('Rekkefølge'), default=30)
    display = models.BooleanField(_('Vis til bedrift'), default=True)
    feedback = models.ForeignKey(
        Feedback,
        related_name='multiple_choice_questions',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.multiple_choice_relation.label

    class Meta(object):
        permissions = (
            ('view_multiplechoicerelation', 'View MultipleChoiceRelation'),
        )
        default_permissions = ('add', 'change', 'delete')


class Choice(models.Model):
    question = models.ForeignKey(
        MultipleChoiceQuestion,
        related_name="choices",
        on_delete=models.CASCADE
    )
    choice = models.CharField(_('valg'), max_length=256, blank=False)

    def __str__(self):
        return self.choice

    class Meta(object):
        permissions = (
            ('view_choice', 'View Choice'),
        )
        default_permissions = ('add', 'change', 'delete')


class MultipleChoiceAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="multiple_choice_answers",
        on_delete=models.CASCADE
    )
    answer = models.CharField(_('svar'), blank=False, max_length=256)
    question = models.ForeignKey(
        MultipleChoiceRelation,
        related_name='answer',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.answer

    @property
    def order(self):
        return self.question.order

    class Meta(object):
        permissions = (
            ('view_multiplechoiceanswer', 'View MultipleChoiceAnswer'),
        )
        default_permissions = ('add', 'change', 'delete')


# For creating a link for others(companies) to see the results page
class RegisterToken(models.Model):
    fbr = models.ForeignKey(
        FeedbackRelation,
        related_name="Feedback_relation",
        on_delete=models.CASCADE
    )
    token = models.CharField(_("token"), max_length=32)
    created = models.DateTimeField(_("opprettet dato"), editable=False, auto_now_add=True)

    def is_valid(self, feedback_relation):
        return self.token == RegisterToken.objects.get(fbr=feedback_relation).token

        # valid_period = datetime.timedelta(days=365)#1 year
        # now = timezone.now()
        # return now < self.created + valid_period

    class Meta(object):
        permissions = (
            ('view_feedbackregistertoken', 'View FeedbackRegisterToken'),
        )
        default_permissions = ('add', 'change', 'delete')
