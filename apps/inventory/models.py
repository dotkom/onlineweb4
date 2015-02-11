# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _

class Item(models.Model):

    name = models.CharField(_(u"Varetype"), max_length=50)

    @property
    def oldest_expiration_date(self):
        return self.batches.all().order_by("expiration_date")[0].expiration_date

    @property
    def last_added(self):
        return self.batches.all().order_by("-date_added")[0].date_added

    @property
    def total_amount(self):
        return sum([batch.amount for batch in self.batches.all()])

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Vare")
        verbose_name_plural = _(u"Varer")

class Batch(models.Model):

    item = models.ForeignKey(Item, verbose_name=_(u"Vare"), related_name="batches")
    amount = models.IntegerField(_(u"Antall"), default = 0)
    date_added = models.DateField(_(u"Dato lagt til"), editable = False, auto_now_add = True)
    expiration_date = models.DateField(_(u"Utløpsdato"), null=True, blank=True, editable = True)

    class Meta:
        verbose_name = _(u"Batch")
        verbose_name_plural = _(u"Batches")

