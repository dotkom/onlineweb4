#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class FeedbackToObjectRelation(models.Model):
    feedback_id = models.OneToOneField(
                    'Feedback')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    answered = models.ManyToManyField(User, related_name='feedbacks', blank=True, null=True)

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
