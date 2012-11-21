#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class FeedbackRelation(models.Model):
    feedback_id = models.OneToOneField('Feedback')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    answered = models.ManyToManyField(
        User,
        related_name='feedbacks',
        blank=True,
        null=True)

    class Meta:
        unique_together = ('feedback_id', 'content_type', 'object_id')

    def __unicode__(self):
        return str(self.feedback_id) + ': ' + str(self.content_object)


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, related_name='oppretter')
    description = models.CharField(_('beskrivelse'), max_length=100)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = _('tilbakemelding')
        verbose_name_plural = _('tilbakemeldinger')


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(_('beskrivelse'), max_length=100)

    def __unicode__(self):
        return self.description


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answer')


FIELD_OF_STUDY_CHOICES = (
    (0, _('Bachelor i Informatikk (BIT)')),
    (1, _('Intelligente Systemer (IRS)')),
    (2, _('Software (SW')),
    (3, _('Informasjonsforvaltning (DIF)')),
    (4, _('Komplekse Datasystemer (KDS)')),
    (5, _('Spillteknologi (SPT)')),
)


class FieldOfStudyQuestion(Question):
    feedback = models.OneToOneField(
        Feedback,
        primary_key=True,
        related_name='field_of_studys')
    field_of_study = models.SmallIntegerField(
        _('Studieretning'),
        choices=FIELD_OF_STUDY_CHOICES,
        default=0)


class FieldOfStudyAnswer(Answer):
    answer = models.SmallIntegerField(
        _('Studieretning'),
        choices=FIELD_OF_STUDY_CHOICES,
        default=0)
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="field_of_study_answers")


class TextQuestion(Question):
    feedback = models.ForeignKey(Feedback, related_name='texts')
    label = models.TextField(_(u'Spørsmål'), blank=False)


class TextAnswer(Answer):
    answer = models.TextField(_('svar'), blank=False)
    feedback_relation = models.ForeignKey(
        FeedbackRelation,
        related_name="text_answers")
