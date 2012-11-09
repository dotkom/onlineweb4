#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, related_name='oppretter')
    description = models.CharField(_('beskrivelse'), max_length=100)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = _('tilbakemelding')
        verbose_name_plural = _('tilbakemeldinger')


# Below this line are feedback "modules" classed that are used to create
# customized feedback forms.
class FieldOfStudy(models.Model):
    CHOICES = (
        (0, _('Bachelor i Informatikk (BIT)')),
        (1, _('Intelligente Systemer (IRS)')),
        (2, _('Software (SW')),
        (3, _('Informasjonsforvaltning (DIF)')),
        (4, _('Komplekse Datasystemer (KDS)')),
        (5, _('Spillteknologi (SPT)')),
    )

    feedback = models.OneToOneField(
        Feedback,
        primary_key=True,
        related_name='field_of_study')
    field_of_study = models.SmallIntegerField(_('Studieretning'), choices=CHOICES, default=0)

class Text(models.Model):
    id = models.AutoField(primary_key=True)
    feedback = models.ForeignKey(Feedback, related_name='text')
    label = models.TextField(_(u'Spørsmål'), blank=False)

    def __unicode__(self):
        return self.label
