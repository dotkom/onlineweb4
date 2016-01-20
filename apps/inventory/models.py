# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone


class Item(models.Model):

    name = models.CharField(_("Varetype"), max_length=50)

    @property
    def oldest_expiration_date(self):
        batches = self.batches.all().order_by("expiration_date")
        if batches:
            return batches[0].expiration_date
        else:
            return None

    @property
    def last_added(self):
        batches = self.batches.all().order_by("-date_added")
        if batches:
            return batches[0].date_added
        else:
            return None

    @property
    def total_amount(self):
        return sum([batch.amount for batch in self.batches.all()])

    @property
    def has_expired_batch(self):
        if timezone.now().date() >= self.oldest_expiration_date:
            return True
        return False

    def __str__(self):
        return self.name

    class Meta(object):
        verbose_name = _("Vare")
        verbose_name_plural = _("Varer")
        permissions = (
            ("view_item", "View Inventory Item"),
        )


class Batch(models.Model):

    item = models.ForeignKey(Item, verbose_name=_("Vare"), related_name="batches")
    amount = models.IntegerField(_("Antall"), default=0)
    date_added = models.DateField(_("Dato lagt til"), editable=False, auto_now_add=True)
    expiration_date = models.DateField(_("Utløpsdato"), null=True, blank=True, editable=True)

    class Meta(object):
        verbose_name = _("Batch")
        verbose_name_plural = _("Batches")
