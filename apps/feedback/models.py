#-*- coding: utf-8 -*-
'''
An anonymous customizable Feedback Schema application.

An Object is connected to a customizable Feedback through FeedbackRelation,
A Feedback can have many Questions.
An Answer is related to an Object and a Question.

This implementation is not very database friendly however, as it does
very many database lookups.
'''
import uuid

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import FIELD_OF_STUDY_CHOICES

import reversion

class FeedbackRelation(models.Model):
    """
    A many to many relation between a Generic Object and a Feedback schema.
    """
    feedback = models.ForeignKey('Feedback')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    deadline = models.DateField()
    gives_mark = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    first_mail_sent = models.BooleanField(default=False)

    # Keep a record of who has answered. (not /what/ they have answered)
    answered = models.ManyToManyField(
        User,
        related_name='feedbacks',
        blank=True,
        null=True)

    class Meta:
        unique_together = ('feedback', 'content_type', 'object_id')

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
            return _(u"Tilbakemelding: " + self.content_title())
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

    def __unicode__(self):
        return str(self.feedback_id) + ': ' + unicode(self.content_object)

    def get_absolute_url(self):
        """
        Returns the absolute URL to its `views.feedback`
        """
        return reverse("apps.feedback.views.feedback",
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
            False

    def save(self, *args, **kwargs):
        new_fbr = not self.pk
        super(FeedbackRelation, self).save(*args, **kwargs)
        if new_fbr:
            token = uuid.uuid4().hex
            rt = RegisterToken(fbr = self, token = token)
            rt.save()


reversion.register(FeedbackRelation)


class Feedback(models.Model):
    """
    A customizable Feedback schema.
    """
    feedback_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User)
    description = models.CharField(_(u'beskrivelse'), max_length=100)
    display_field_of_study = models.BooleanField(_(u'Vis studie oversikt'), default=True, 
        help_text =_(u'Grafen over studiefelt vil bli vist til bedriften'))
 
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

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = _(u'tilbakemeldingsskjema')
        verbose_name_plural = _(u'tilbakemeldingsskjemaer')


reversion.register(Feedback)


class FieldOfStudyAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="field_of_study_answers")

    answer = models.SmallIntegerField(
        _(u'Studieretning'), choices = FIELD_OF_STUDY_CHOICES)

    def __unicode__(self):
        return self.get_answer_display()


reversion.register(FieldOfStudyAnswer)


class TextQuestion(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        related_name='text_questions')

    order = models.SmallIntegerField(_(u'Rekkefølge'), default=10)
    label = models.CharField(_(u'Spørsmål'), blank=False, max_length=256)
    display = models.BooleanField(_(u'Vis til bedrift'), default=True)


    def __unicode__(self):
        return self.label


reversion.register(TextQuestion)


class TextAnswer(models.Model):
    question = models.ForeignKey(TextQuestion, related_name='answer')

    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="text_answers")

    answer = models.TextField(_(u'svar'), blank=False)

    def __unicode__(self):
        return self.answer

    @property
    def order(self):
        return self.question.order


reversion.register(TextAnswer)


RATING_CHOICES = [(k, str(k)) for k in range(1, 7)]  # 1 to 6


class RatingQuestion(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        related_name='rating_questions')

    order = models.SmallIntegerField(_(u'Rekkefølge'), default=20)
    label = models.CharField(_(u'Spørsmål'), blank=False, max_length=256)
    display = models.BooleanField(_(u'Vis til bedrift'), default=True)

    def __unicode__(self):
        return self.label


reversion.register(RatingQuestion)


class RatingAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="rating_answers")

    answer = models.SmallIntegerField(
        _(u'karakter'),
        choices=RATING_CHOICES,
        default=0)

    question = models.ForeignKey(RatingQuestion, related_name='answer')

    def __unicode__(self):
        return self.get_answer_display()

    @property
    def order(self):
        return self.question.order


reversion.register(RatingAnswer)

    
class MultipleChoiceQuestion(models.Model):
    label = models.CharField(_(u'Spørsmål'), blank=False, max_length=256)

    class Meta:
        verbose_name = _(u'Flervalgspørsmål')
        verbose_name_plural = _(u'Flervalgspørsmål')

    def __unicode__(self):
        return self.label


reversion.register(MultipleChoiceQuestion)


class MultipleChoiceRelation(models.Model):
    multiple_choice_relation = models.ForeignKey(MultipleChoiceQuestion)
    order = models.SmallIntegerField(_(u'Rekkefølge'), default=30)
    display = models.BooleanField(_(u'Vis til bedrift'), default=True)
    feedback = models.ForeignKey(Feedback, related_name='multiple_choice_questions')

    def __unicode__(self):
        return self.multiple_choice_relation.label


reversion.register(MultipleChoiceRelation)


class Choice(models.Model):
    question = models.ForeignKey(MultipleChoiceQuestion, related_name="choices")
    choice = models.CharField(_(u'valg'), max_length=256, blank=False)

    def __unicode__(self):
        return self.choice


reversion.register(Choice)


class MultipleChoiceAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="multiple_choice_answers")

    answer = models.CharField(_(u'svar'), blank=False, max_length=256)
    question = models.ForeignKey(MultipleChoiceRelation, related_name='answer')

    def __unicode__(self):
        return self.answer

    @property
    def order(self):
        return self.question.order


reversion.register(MultipleChoiceAnswer)


#For creating a link for others(companies) to see the results page
class RegisterToken(models.Model):
    fbr = models.ForeignKey(FeedbackRelation, related_name="Feedback_relation")
    token = models.CharField(_(u"token"), max_length=32)
    created = models.DateTimeField(_(u"opprettet dato"), editable=False, auto_now_add=True)

    def is_valid(self, feedback_relation):
        return self.token == RegisterToken.objects.get(fbr=feedback_relation).token
        
        #valid_period = datetime.timedelta(days=365)#1 year
        #now = timezone.now()
        #return now < self.created + valid_period


reversion.register(RegisterToken)
