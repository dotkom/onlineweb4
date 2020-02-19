# -*- coding: utf-8 -*-
"""
An anonymous customizable Feedback Schema application.

An Object is connected to a customizable Feedback through FeedbackRelation,
A Feedback can have many Questions.
An Answer is related to an Object and a Question.

This implementation is not very database friendly however, as it does
very many database lookups.
"""
import uuid
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext as _

from apps.authentication.constants import FieldOfStudyType
from apps.authentication.models import OnlineUser

User = settings.AUTH_USER_MODEL


class FeedbackRelationManager(models.Manager):
    def can_answer(self, user: User):
        queryset = (
            self.get_queryset().filter(active=True).prefetch_related("content_object")
        )
        can_answer_ids = [fbr.can_answer(user) for fbr in queryset.all()]
        return queryset.filter(pk__in=can_answer_ids)


class FeedbackRelation(models.Model):
    """
    A many to many relation between a Generic Object and a Feedback schema.
    """

    objects = FeedbackRelationManager()

    feedback = models.ForeignKey(
        "Feedback", verbose_name=_("Tilbakemeldingskjema"), on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    deadline = models.DateField(_("Tidsfrist"))
    gives_mark = models.BooleanField(
        _("Gir Prikk"),
        default=True,
        help_text=_(
            "Gir automatisk prikk til brukere som ikke har svart innen fristen"
        ),
    )
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    first_mail_sent = models.BooleanField(default=False)

    # Keep a record of who has answered. (not /what/ they have answered)
    answered = models.ManyToManyField(User, related_name="feedbacks", blank=True)

    class Meta:
        unique_together = ("feedback", "content_type", "object_id")

        permissions = (("view_feedbackrelation", "View FeedbackRelation"),)
        default_permissions = ("add", "change", "delete")

        verbose_name = _("tilbakemelding")
        verbose_name_plural = _("tilbakemeldinger")

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
        return str(self.feedback_id) + ": " + str(self.content_object)

    def get_absolute_url(self):
        """
        Returns the absolute URL to its `views.feedback`
        """
        return reverse(
            "feedback",
            args=[
                self.content_type.app_label,
                self.content_type.model,
                self.object_id,
                self.feedback.feedback_id,
            ],
        )

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
            return _("Du har allerede svart på skjemaet.")

        if hasattr(self.content_object, "feedback_users"):
            if self.content_object.feedback_users():
                if user not in self.content_object.feedback_users():
                    return _("Du har ikke tilgang til å svare på dette skjemaet.")
            else:
                return _("Skjemaet har ingen brukere som kan svare på skjemaet.")

        return _("Ukjent feil.")

    def not_answered(self):
        if hasattr(self.content_object, "feedback_users"):
            return set(self.content_object.feedback_users()).difference(
                set(self.answered.all())
            )
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


class Feedback(models.Model):
    """
    A customizable Feedback schema.
    """

    feedback_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(_("beskrivelse"), max_length=100)
    display_field_of_study = models.BooleanField(
        _("Vis studieoversikt"),
        default=True,
        help_text=_("Grafen over studiefelt vil bli vist til bedriften"),
    )
    display_info = models.BooleanField(
        _("Vis extra informasjon"),
        default=True,
        help_text=_("En boks med ekstra informasjon vil bli vist til bedriften"),
    )
    available = models.BooleanField(
        _("Vis feedbackskjemaet"),
        default=True,
        help_text=_(
            "Dette brukes til å skjule ubrukte skjemaer, lager du et nytt, så ignorer denne."
        ),
    )

    @property
    def id(self):
        return self.feedback_id

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
        verbose_name = _("tilbakemeldingsskjema")
        verbose_name_plural = _("tilbakemeldingsskjemaer")
        permissions = (("view_feedback", "View Feedback"),)
        default_permissions = ("add", "change", "delete")


class GenericSurvey(models.Model):
    """
    A Generic survey that may be answered by a specific set of users.
    """

    title = models.CharField(max_length=128, verbose_name=_("Tittel"))
    feedback = models.ForeignKey(
        to=Feedback,
        related_name="generic_survey",
        verbose_name=_("Undersøkelsesmal"),
        on_delete=models.CASCADE,
    )
    deadline = models.DateField(_("Tidsfrist"))
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Opprettet dato")
    )
    allowed_users = models.ManyToManyField(
        to=User,
        related_name="allowed_generic_surveys",
        verbose_name=_("Brukere som kan svare"),
        blank=True,
    )
    owner = models.ForeignKey(
        to=User,
        related_name="owned_generic_surveys",
        verbose_name=_("Eier"),
        on_delete=models.DO_NOTHING,
    )
    owner_group = models.ForeignKey(
        to=Group,
        related_name="owned_generic_surveys",
        verbose_name=_("Eiergruppe"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    feedback_relation = GenericRelation(FeedbackRelation)

    def get_feedback_relation(self):
        return FeedbackRelation.objects.get(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id
        )

    def feedback_users(self):
        if self.allowed_users.exists():
            return self.allowed_users.all()
        else:
            return OnlineUser.objects.all()

    def feedback_email(self):
        if (
            self.owner_group
            and self.owner_group.online_group
            and self.owner_group.online_group.email
        ):
            return self.owner_group.online_group.email
        else:
            return self.owner.primary_email

    def feedback_title(self):
        return self.title

    def feedback_date(self):
        return self.created_date

    def feedback_info(self):
        info = OrderedDict()
        info[_("Antall mulig svar")] = len(self.feedback_users())
        return info

    class Meta:
        verbose_name = _("Generisk undersøkelse")
        verbose_name_plural = _("Generiske undersøkelser")
        ordering = ("created_date", "title")


class Question(models.Model):
    order = models.SmallIntegerField(_("Rekkefølge"), default=0)
    display = models.BooleanField(_("Vis til bedrift"), default=True)
    required = models.BooleanField(_("Pålagt"), default=True)
    help_text = models.CharField(_("Utdypning"), blank=True, max_length=256)

    class Meta:
        abstract = True


class FieldOfStudyAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="field_of_study_answers",
        on_delete=models.CASCADE,
    )
    answer = models.SmallIntegerField(
        _("Studieretning"), choices=FieldOfStudyType.ALL_CHOICES
    )

    def __str__(self):
        return self.get_answer_display()

    class Meta:
        verbose_name = _("Studieretningssvar")
        verbose_name_plural = _("Studieretningssvar")
        permissions = (("view_fieldofstudyanswer", "View FieldOfStudyAnswer"),)
        default_permissions = ("add", "change", "delete")


class TextQuestion(Question, models.Model):
    feedback = models.ForeignKey(
        Feedback, related_name="text_questions", on_delete=models.CASCADE
    )
    order = models.SmallIntegerField(_("Rekkefølge"), default=10)
    label = models.CharField(_("Spørsmål"), blank=False, max_length=256)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _("Tekstspørsmål")
        verbose_name_plural = _("Tekstspørsmål")
        permissions = (("view_textquestion", "View TextQuestion"),)
        default_permissions = ("add", "change", "delete")


class TextAnswer(models.Model):
    question = models.ForeignKey(
        TextQuestion, related_name="answer", on_delete=models.CASCADE
    )
    feedback_relation = models.ForeignKey(
        FeedbackRelation, related_name="text_answers", on_delete=models.CASCADE
    )

    answer = models.TextField(_("svar"))

    def __str__(self):
        return self.answer

    @property
    def order(self):
        return self.question.order

    class Meta:
        verbose_name = _("Tekstsvar")
        verbose_name_plural = _("Tekstsvar")
        permissions = (("view_textanswer", "View TextAnswer"),)
        default_permissions = ("add", "change", "delete")


RATING_CHOICES = [(k, str(k)) for k in range(1, 7)]  # 1 to 6
RATING_CHOICES.insert(
    0, ("", "")
)  # Adds a blank field to prevent 1 from beeing selected by default


class RatingQuestion(Question, models.Model):
    feedback = models.ForeignKey(
        Feedback, related_name="rating_questions", on_delete=models.CASCADE
    )
    order = models.SmallIntegerField(_("Rekkefølge"), default=20)
    label = models.CharField(_("Spørsmål"), blank=False, max_length=256)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _("Vurderingsspørsmål")
        verbose_name_plural = _("Vurderingsspørsmål")
        permissions = (("view_ratingquestion", "View RatingQuestion"),)
        default_permissions = ("add", "change", "delete")


class RatingAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation, related_name="rating_answers", on_delete=models.CASCADE
    )
    answer = models.SmallIntegerField(_("karakter"), choices=RATING_CHOICES, default=0)

    question = models.ForeignKey(
        RatingQuestion, related_name="answer", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.get_answer_display()

    @property
    def order(self):
        return self.question.order

    class Meta:
        verbose_name = _("Vurderingssvar")
        verbose_name_plural = _("Vurderingssvar")
        permissions = (("view_ratinganswer", "View RatingAnswer"),)
        default_permissions = ("add", "change", "delete")


class MultipleChoiceQuestion(models.Model):
    label = models.CharField(_("Spørsmål"), blank=False, max_length=256)

    class Meta:
        verbose_name = _("Flervalgspørsmål")
        verbose_name_plural = _("Flervalgspørsmål")
        permissions = (("view_multiplechoicequestion", "View MultipleChoiceQuestion"),)
        default_permissions = ("add", "change", "delete")


class MultipleChoiceRelation(Question, models.Model):
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE)
    order = models.SmallIntegerField(_("Rekkefølge"), default=30)
    feedback = models.ForeignKey(
        Feedback, related_name="multiple_choice_questions", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.question.label

    class Meta:
        verbose_name = _("Flervalgsrelasjon")
        verbose_name_plural = _("Flervalgsrelasjoner")
        permissions = (("view_multiplechoicerelation", "View MultipleChoiceRelation"),)
        default_permissions = ("add", "change", "delete")


class Choice(models.Model):
    question = models.ForeignKey(
        MultipleChoiceQuestion, related_name="choices", on_delete=models.CASCADE
    )
    choice = models.CharField(_("valg"), max_length=256, blank=False)

    def __str__(self):
        return self.choice

    class Meta:
        verbose_name = _("Valg")
        verbose_name_plural = _("Valg")
        permissions = (("view_choice", "View Choice"),)
        default_permissions = ("add", "change", "delete")


class MultipleChoiceAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="multiple_choice_answers",
        on_delete=models.CASCADE,
    )
    answer = models.CharField(_("svar"), blank=False, max_length=256)
    question = models.ForeignKey(
        MultipleChoiceRelation, related_name="answer", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.answer

    @property
    def order(self):
        return self.question.order

    class Meta:
        verbose_name = _("Flervalgssvar")
        verbose_name_plural = _("Flervalgssvar")
        permissions = (("view_multiplechoiceanswer", "View MultipleChoiceAnswer"),)
        default_permissions = ("add", "change", "delete")


# For creating a link for others(companies) to see the results page
class RegisterToken(models.Model):
    fbr = models.ForeignKey(
        FeedbackRelation, related_name="token_objects", on_delete=models.CASCADE
    )
    token = models.UUIDField(
        _("Token"), editable=False, unique=True, default=uuid.uuid4
    )
    created = models.DateTimeField(
        _("opprettet dato"), editable=False, auto_now_add=True
    )

    def is_valid(self, feedback_relation):
        return self.token == RegisterToken.objects.get(fbr=feedback_relation).token

        # valid_period = datetime.timedelta(days=365)#1 year
        # now = timezone.now()
        # return now < self.created + valid_period

    class Meta:
        permissions = (("view_feedbackregistertoken", "View FeedbackRegisterToken"),)
        default_permissions = ("add", "change", "delete")
