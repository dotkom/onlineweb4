# -*- coding: utf-8 -*-

from apps.authentication.models import OnlineUser as User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Privacy(models.Model):
    visible_for_other_users = models.BooleanField(_(u"profil synlig for andre brukere"), default=True)
    expose_username = models.BooleanField(_(u"vis brukernavn"), default=True)
    expose_email = models.BooleanField(_(u"vis epost"), default=True)
    expose_first_name = models.BooleanField(_(u"vis fornavn"), default=True)
    expose_last_name = models.BooleanField(_(u"vis etternavn"), default=True)
    expose_field_of_study = models.BooleanField(_(u"vis studieretning"), default=True)
    expose_started_date = models.BooleanField(_(u"vis studiestartdato"), default=True)
    expose_compiled = models.BooleanField(_(u"vis kompilert dato"), default=True)
    expose_phone_number = models.BooleanField(_(u"vis telefonnummer"), default=True)
    expose_address = models.BooleanField(_(u"vis addresse"), default=True)

    user = models.ForeignKey(User, unique=True, related_name="privacy")

    def __unicode__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = _(u"personvern")
        verbose_name_plural = _(u"personvern")