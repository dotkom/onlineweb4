# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from datetime import datetime, timedelta

from django.contrib.auth.models import Group
from apps.authentication.models import OnlineUser as User
from apps.companyprofile.models import Company
from apps.events.models import Event


class OrderMixin(models.Model):
    order_type = models.IntegerField( choices=(
        (1, 'Plakat'),
        (2, 'Bong'),
        (3, 'Annet'),
    ))
    ordered_date = models.DateTimeField(auto_now_add=True, editable=False)
    ordered_by = models.ForeignKey(User, related_name=_(u"bestilt av"))
    ordered_committee = models.ForeignKey(Group, related_name=_(u'bestilt av komite'))
    assigned_to = models.ForeignKey(User, related_name=_(u'tilordnet til'), blank=True, null=True)
    comments = models.TextField(_(u"kommentar"), max_length=500, blank=True, null=True)
    amount = models.IntegerField(_(u'antall opplag'), blank=True, null=True)
    finished = models.BooleanField(_(u"ferdig"), default=False)


class EventMixin(OrderMixin):
    event = models.ForeignKey(Event, related_name=u'Arrangement')


class Poster(EventMixin):
    description = models.TextField(_(u"beskrivelse"), max_length=1000)
    price = models.DecimalField(_(u'pris'), max_digits=10, decimal_places=2, blank=True, null=True)
    display_from = models.DateField(_(u"vis fra"))
    display_to = models.DateField(_(u"vis til"))

    class Meta:
        ordering = ['-id']
        verbose_name = _(u"plakatbestilling")
        verbose_name_plural = _(u"plakatbestillinger")
        permissions = (
            ('add_poster_order', 'Add poster orders'),
            ('overview_poster_order', 'View poster order overview'),
            ('view_poster_order', 'View poster orders'),
        )

    def __str__(self):
        return "Plakatbestilling: %(event)s" % {'event': self.event}

    def poster_up(self):
        return self.finished and self.display_from < datetime.now().date() < self.display_to


class Freestyle(OrderMixin):
    description = models.TextField(_(u'beskrivelse'), max_length=1000)

    def __str__(self):
        return "Freestyle: %s..." % self.description[:15]


class CustomText(models.Model):
    field = models.CharField(max_length=50)
    text = models.CharField(max_length=30)
