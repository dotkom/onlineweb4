# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.contrib.auth.models import Group
from apps.events.models import Event


User = settings.AUTH_USER_MODEL


class OrderMixin(models.Model):
    """
    A mixin for all orders.
    Handles most fields, and brings some basic functionality.

    ordered_by and ordered_committee will get set automatically based on submitting user.
    amount and description is optional, but should exist in all orders.
    assigned_to and finished will be set by ProKom.
    """
    order_type = models.IntegerField(choices=(
        (1, 'Plakat'),
        (2, 'Bong'),
        (3, 'Annet'),
    ))
    ordered_date = models.DateTimeField(auto_now_add=True, editable=False)
    ordered_by = models.ForeignKey(User, verbose_name=_(u"bestilt av"), related_name='ordered_by')
    ordered_committee = models.ForeignKey(
        Group,
        verbose_name=_(u'bestilt av komite'),
        related_name='ordered_committee'
    )
    assigned_to = models.ForeignKey(
        User,
        verbose_name=_(u'tilordnet til'),
        related_name='assigned_to',
        blank=True,
        null=True
    )
    description = models.TextField(_(u"beskrivelse"), max_length=1000, blank=True, null=True)
    amount = models.IntegerField(_(u'antall opplag'), blank=True, null=True)
    finished = models.BooleanField(_(u"ferdig"), default=False)
    display_from = models.DateField(_(u"vis fra"), blank=True, null=True, default=None)

    def toggle_finished(self):
        self.finished = not self.finished
        self.save()

    def get_absolute_url(self):
        return reverse('posters_detail', args=[str(self.id)])

    def get_dashboard_url(self):
        return self.get_absolute_url()

    class Meta(object):

        permissions = (
            ('add_poster_order', 'Add poster orders'),
            ('overview_poster_order', 'View poster order overview'),
            ('view_poster_order', 'View poster orders'),
        )


class Poster(OrderMixin):
    """
    Poster order
    """
    title = models.CharField(_(u'arrangementstittel'), max_length=60, blank=True, null=True)
    event = models.ForeignKey(Event, related_name=u'Arrangement', blank=True, null=True)
    price = models.DecimalField(_(u'pris'), max_digits=10, decimal_places=2, blank=True, null=True)
    display_to = models.DateField(_(u"vis til"), blank=True, null=True, default=None)
    bong = models.IntegerField(_(u'bonger'), blank=True, null=True)

    class Meta(object):
        ordering = ['-id']
        verbose_name = _(u"bestilling")
        verbose_name_plural = _(u"bestillinger")
        permissions = (
            ('add_poster_order', 'Add poster orders'),
            ('overview_poster_order', 'View poster order overview'),
            ('view_poster_order', 'View poster orders'),
        )

    def __str__(self):
        if self.order_type == 1:
            return _(u"Plakatbestilling: %(event)s" % {'event': self.event.title})
        else:
            return _(u"Generell bestilling: %(title)s" % {'title': self.title})

    def __unicode__(self):
        return self.__str__()


class CustomText(models.Model):
    field = models.CharField(max_length=50)
    text = models.CharField(max_length=30)
