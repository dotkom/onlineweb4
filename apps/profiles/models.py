# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


User = settings.AUTH_USER_MODEL


class Privacy(models.Model):
    visible_for_other_users = models.BooleanField(_("profil synlig for andre brukere"), default=True)
    expose_nickname = models.BooleanField(_("vis kallenavn"), default=True)
    expose_email = models.BooleanField(_("vis epost"), default=True)
    expose_phone_number = models.BooleanField(_("vis telefonnummer"), default=True)
    expose_address = models.BooleanField(_("vis addresse"), default=True)

    user = models.OneToOneField(User, related_name="privacy")

    def __str__(self):
        return self.user.get_full_name()

    class Meta(object):
        verbose_name = _("personvern")
        verbose_name_plural = _("personvern")
        permissions = (
            ('view_privacy', 'View Privacy'),
        )
