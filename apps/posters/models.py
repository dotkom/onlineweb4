# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from datetime import datetime, timedelta

from django.contrib.auth.models import Group
from apps.authentication.models import OnlineUser as User
from apps.companyprofile.models import Company
from apps.events.models import Event


class OrderMixin(models.Model):
    """
    A mixin for all orders.
    Handles most fields, and brings some basic functionality.

    ordered_by and ordered_committee will get set automatically based on submitting user.
    amount and description is optional, but should exist in all orders.
    assigned_to and finished will be set by ProKom.
    """
    order_type = models.IntegerField( choices=(
        (1, 'Plakat'),
        (2, 'Bong'),
        (3, 'Annet'),
    ))
    permissions = (
        ('add_poster_order', 'Add poster orders'),
        ('overview_poster_order', 'View poster order overview'),
        ('view_poster_order', 'View poster orders'),
    )
    ordered_date = models.DateTimeField(auto_now_add=True, editable=False)
    ordered_by = models.ForeignKey(User, related_name=_(u"bestilt av"))
    ordered_committee = models.ForeignKey(Group, related_name=_(u'bestilt av komite'))
    assigned_to = models.ForeignKey(User, related_name=_(u'tilordnet til'), blank=True, null=True)
    description = models.TextField(_(u"beskrivelse"), max_length=1000, blank=True, null=True)
    amount = models.IntegerField(_(u'antall opplag'), blank=True, null=True)
    finished = models.BooleanField(_(u"ferdig"), default=False)
    display_from = models.DateField(_(u"vis fra"), blank=True, null=True, default=None)

    def toggle_finished(self):
        self.finished = not self.finished
        self.save()


class EventMixin(OrderMixin):
    """
    Mixin for all orders requring an event.
    """
    event = models.ForeignKey(Event, related_name=u'Arrangement')


class GeneralOrder(OrderMixin):
    """
    General order, basically an order that does not have a corresponding event.
    """
    title = models.CharField(_(u'arrangementstittel'), max_length=60)

    class Meta:
        ordering = ['-id']
        verbose_name = _(u"generell bestilling")
        verbose_name_plural = _(u"generelle bestillinger")

    def __str__(self):
        return "Generell bestilling: %(event)s" % {'event': self.event}


class Poster(EventMixin):
    """
    Poster order
    """
    price = models.DecimalField(_(u'pris'), max_digits=10, decimal_places=2, blank=True, null=True)
    display_to = models.DateField(_(u"vis til"), blank=True, null=True, default=None)
    bong = models.IntegerField(_(u'bonger'), blank=True, null=True)

    class Meta:
        ordering = ['-id']
        verbose_name = _(u"plakatbestilling")
        verbose_name_plural = _(u"plakatbestillinger")

    def __str__(self):
        return "Plakatbestilling: %(event)s" % {'event': self.event}



class CustomText(models.Model):
    field = models.CharField(max_length=50)
    text = models.CharField(max_length=30)
