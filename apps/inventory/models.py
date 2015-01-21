# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _

class Item(models.Model):

    name = models.CharField(_(u"Vare"), max_length=50)
    amount = models.IntegerField(_(u"Antall"))
    expiration_date = models.DateField(_(u"Eldste Utløpsdato"), null=True, blank=True, editable=True)


    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Vare")
        verbose_name_plural = _(u"Varer")