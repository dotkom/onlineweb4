#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class FeedbackRelation(models.Model):
    feedback = models.ForeignKey('Feedback')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    answered = models.ManyToManyField(
        User,
        related_name='feedbacks',
        blank=True,
        null=True)

    @property
    def questions(self):
        return self.feedback.questions

    @property
    def answers(self):
        """
        When creating more Question types, add their answers here
        """
        answers = []
        answers.extend(self.field_of_study_answers.all())
        answers.extend(self.text_answers.all())
        return sorted(answers, key=lambda x: x.order)

    def answers_to_question(self, question):
        return question.answer.filter(feedback_relation=self)

    class Meta:
        unique_together = ('feedback', 'content_type', 'object_id')

    def __unicode__(self):
        return str(self.feedback_id) + ': ' + str(self.content_object)


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, related_name='oppretter')
    description = models.CharField(_('beskrivelse'), max_length=100)

    @property
    def questions(self):
        """
        When creating more Question types, add them here
        """
        questions = []
        questions.extend(self.field_of_study_questions.all())
        questions.extend(self.text_questions.all())
        return sorted(questions, key=lambda x: x.order)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = _('tilbakemelding')
        verbose_name_plural = _('tilbakemeldinger')


FIELD_OF_STUDY_CHOICES = (
    (0, _('Bachelor i Informatikk (BIT)')),
    (1, _('Intelligente Systemer (IRS)')),
    (2, _('Software (SW)')),
    (3, _('Informasjonsforvaltning (DIF)')),
    (4, _('Komplekse Datasystemer (KDS)')),
    (5, _('Spillteknologi (SPT)')),
)


class FieldOfStudyQuestion(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        primary_key=True,
        related_name='field_of_study_questions')

    order = models.SmallIntegerField(_(u'Rekkefølge'), default=1)

    field_of_study = models.SmallIntegerField(
        _('Studieretning'),
        choices=FIELD_OF_STUDY_CHOICES,
        default=0)

    def __unicode__(self):
        return "Studieretning"


class FieldOfStudyAnswer(models.Model):
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="field_of_study_answers")

    answer = models.SmallIntegerField(
        _('Studieretning'),
        choices=FIELD_OF_STUDY_CHOICES,
        default=0)

    question = models.ForeignKey(FieldOfStudyQuestion, related_name='answer')

    def __unicode__(self):
        return str(self.question) + ": " + self.answer

    @property
    def order(self):
        return self.question.order


class TextQuestion(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        related_name='text_questions')

    order = models.SmallIntegerField(_(u'Rekkefølge'), default=10)

    label = models.CharField(_(u'Spørsmål'), blank=False, max_length=256)

    def __unicode__(self):
        return self.label


class TextAnswer(models.Model):
    question = models.ForeignKey(TextQuestion, related_name='answer')

    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="text_answers")

    answer = models.TextField(_('svar'), blank=False)

    def __unicode__(self):
        return str(self.question) + ": " + self.answer

    @property
    def order(self):
        return self.question.order
