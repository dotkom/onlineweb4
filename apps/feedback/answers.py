#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from apps.feedback.questions import Question


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answer')


class TextAnswer(Answer):
    answer = models.TextField(_('svar'), blank=False)


class FieldOfStudyAnswer(Answer):
    CHOICES = (
        (0, _('Bachelor i Informatikk (BIT)')),
        (1, _('Intelligente Systemer (IRS)')),
        (2, _('Software (SW')),
        (3, _('Informasjonsforvaltning (DIF)')),
        (4, _('Komplekse Datasystemer (KDS)')),
        (5, _('Spillteknologi (SPT)')),
    )

    answer = models.SmallIntegerField(_('Studieretning'), choices=CHOICES, default=0)
