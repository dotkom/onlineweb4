# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


import reversion


User = settings.AUTH_USER_MODEL


class Privacy(models.Model):
    visible_for_other_users = models.BooleanField(_(u"profil synlig for andre brukere"), default=True)
    expose_nickname = models.BooleanField(_(u"vis kallenavn"), default=True)
    expose_email = models.BooleanField(_(u"vis epost"), default=True)
    expose_phone_number = models.BooleanField(_(u"vis telefonnummer"), default=True)
    expose_address = models.BooleanField(_(u"vis addresse"), default=True)

    user = models.OneToOneField(User, related_name="privacy")

    def __unicode__(self):
        return self.user.get_full_name()

    class Meta(object):
        verbose_name = _(u"personvern")
        verbose_name_plural = _(u"personvern")
        permissions = (
            ('view_privacy', 'View Privacy'),
        )

