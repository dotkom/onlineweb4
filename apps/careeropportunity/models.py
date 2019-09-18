# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager

from apps.companyprofile.models import Company


class CareerOpportunity(models.Model):
    """
    Base class for CareerOpportunity
    """

    company = models.ForeignKey(Company, related_name='company', on_delete=models.CASCADE)
    title = models.CharField(_('tittel'), max_length=100)
    ingress = models.CharField(_('ingress'), max_length=250)
    description = models.TextField(_('beskrivelse'))
    website = models.URLField(_('nettside'), blank=True, null=True)
    start = models.DateTimeField(_('aktiv fra'))
    end = models.DateTimeField(_('aktiv til'))
    featured = models.BooleanField(_('fremhevet'), default=False, blank=True)
    deadline = models.DateTimeField(_('frist'), default=None, null=True, blank=True)

    JOB_TYPE_CHOICES = (
        (1, 'Fastjobb'),
        (2, 'Deltidsjobb'),
        (3, 'Sommerjobb/internship'),
        (4, 'Start-up'),
        (6, 'Graduate'),
        (5, 'Annet'),
    )

    employment = models.IntegerField(
        _('stillingstype'),
        choices=JOB_TYPE_CHOICES,
        blank=False,
        null=False,
    )

    location = TaggableManager(_('sted(er)'), blank=True)
    location.remote_field.related_name = "+"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('karrieremulighet')
        verbose_name_plural = _('karrieremuligheter')
        permissions = (
            ('view_careeropportunity', 'View CareerOpportunity'),
        )
        default_permissions = ('add', 'change', 'delete')
