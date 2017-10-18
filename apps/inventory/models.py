# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.gallery.models import ResponsiveImage


class ItemCategory(models.Model):
    name = models.CharField(_("Kategori"), max_length=50)

    def __str__(self):
        return self.name


class Item(models.Model):

    name = models.CharField(_("Varetype"), max_length=50)
    description = models.CharField(_("Beskrivelse"), max_length=50, null=True, blank=True)
    price = models.IntegerField(_("Pris"), null=True, blank=True)
    available = models.BooleanField(_("Til salgs"), default=False)
    category = models.ForeignKey(ItemCategory, verbose_name=_("Kategori"),
                                 related_name="category", null=True, blank=True)
    image = models.ForeignKey(ResponsiveImage, null=True, blank=True, default=None)

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
        if self.oldest_expiration_date and timezone.now().date() >= self.oldest_expiration_date:
            return True
        return False

    def reduce_stock(self, amount):
        """
        Makes an assumption that the oldest batches are sold first and reduce them first.
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

        self.handle_notifications(amount)

    def handle_notifications(self, amount):

        # Send one notification when the stock goes to or below 10
        if self.total_amount <= 10 and self.total_amount + amount > 10:
            message = "Det er kun " + str(self.total_amount) + " igjen av " + str(self.name) + \
                      " på kontoret.\n\n" \
                      "Dette er en automatisk generert melding og antallet kan være noe feil."

            EmailMessage(
                "[Nibble] Lav stock på " + self.name,
                str(message),
                "online@online.ntnu.no",
                [],
                [settings.EMAIL_TRIKOM]
            ).send()

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
