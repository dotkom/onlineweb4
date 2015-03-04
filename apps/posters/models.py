# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser as User, FIELD_OF_STUDY_CHOICES


class Poster(models.Model):
    title = models.TextField(_(u"tittel"))
    category = models.TextField(_(u"type"))
    description = models.TextField(_(u"beskrivelse"))
    location = models.TextField(_(u"beskrivelse"))
    date = models.DateField(_(u"vises fra"))
    company = models.TextField(_(u"bedrift"))


class Order(object):
    poster = models.ForeignKey(Poster, verbose_name=_(u"plakat"))
    comments = models.TextField(_(u"tittel"))
    ordered_by = models.ForeignKey(User, verbose_name=_(u"bestilt av"))
    contact_email = models.EmailField(_(u"kontaktepost"))
    display_from = models.DateField(_(u"vises fra"))
    display_to = models.DateField(_(u"vises til"))

    class Meta:
        verbose_name = _(u"plakatbestilling")
        verbose_name_plural = _(u"plakatbestillinger")
        permissions = (
            ('view_posters', 'View poster orders'),
            ('add_posters', 'View poster orders'),
        )
