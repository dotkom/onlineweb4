# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone


class ItemCategory(models.Model):
    name = models.CharField(_(u"Kategori"), max_length=50)


class Item(models.Model):

    name = models.CharField(_(u"Varetype"), max_length=50)
    description = models.CharField(_(u"Beskrivelse"), max_length=50, null=True, blank=True)
    price = models.IntegerField(_(u"Pris"), null=True, blank=True)
    avalible = models.BooleanField(_(u"Til salgs"), default=False)
    category = models.ForeignKey(ItemCategory, verbose_name=_(u"Kategori"), related_name="category", null=True, blank=True)

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

    def oldest_batch(self):
        batches = self.batches.filter(amount__gt=0).order_by("date_added")
        if batches:
            return batches[0]
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

    def reduce_stock(self, amount):
        """
        Makes an assumption that the oldes batches are sold first and reduce them first.
        """

        oldest_batch = self.oldest_batch()

        if oldest_batch:
            if oldest_batch.amount > amount:
                oldest_batch.amount = oldest_batch.amount - amount
                oldest_batch.save()
            else:
                diff = amount - oldest_batch.amount
                oldest_batch.amount = 0
                oldest_batch.save()
                self.reduce_stock(diff)

        #TODO notification on low stock


    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = _(u"Vare")
        verbose_name_plural = _(u"Varer")
        permissions = (
            ("view_item", u"View Inventory Item"),
        )


class Batch(models.Model):

    item = models.ForeignKey(Item, verbose_name=_(u"Vare"), related_name="batches")
    amount = models.IntegerField(_(u"Antall"), default=0)
    date_added = models.DateField(_(u"Dato lagt til"), editable=False, auto_now_add=True)
    expiration_date = models.DateField(_(u"Utløpsdato"), null=True, blank=True, editable=True)

    class Meta(object):
        verbose_name = _(u"Batch")
        verbose_name_plural = _(u"Batches")
