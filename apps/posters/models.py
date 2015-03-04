# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _

from django.contrib.auth.models import Group
from apps.authentication.models import OnlineUser as User
from apps.companyprofile.models import Company


class Poster(models.Model):
    POSTER_TYPES = [
        (0, _(u'Plakat')),
        (1, _(u'Banner')),
        (2, _(u'Bong')),
    ]

    # Poster specific
    title = models.TextField(_(u"arrangementstittel"), max_length=50)
    company = models.ForeignKey(Company, related_name=_(u"bedrift"))
    location = models.TextField(_(u"sted"), max_length=50)
    when = models.DateTimeField(_(u'event-start'))
    category = models.IntegerField(_(u"type"), choices=POSTER_TYPES)
    amount = models.IntegerField(_(u'antall'), decimal_places=2, max_digits=10, blank=True, null=True)
    description = models.TextField(_(u"beskrivelse"), max_length=1000)
    price = models.DecimalField(_(u'pris'), blank=True, null=True)
    display_from = models.DateField(_(u"vis fra"))
    display_to = models.DateField(_(u"vis til"))

    # Order specific
    ordered_date = models.DateTimeField(auto_now_add=True, editable=False)
    ordered_by = models.ForeignKey(User, related_name=_(u"bestilt av"))
    ordered_by_group = models.ForeignKey(Group, related_name=_(u'bestilt av komite'))
    assigned_to = models.ForeignKey(User, related_name=_(u'tilordnet til'), blank=True, null=True)
    comments = models.TextField(_(u"kommentar"), max_length=500, blank=True, null=True)


    class Meta:
        verbose_name = _(u"plakatbestilling")
        verbose_name_plural = _(u"plakatbestillinger")
        permissions = (
            ('add_poster_order', 'View poster orders'),
            ('overview_poster_order', 'View poster order overview'),
            ('view_poster_order', 'View poster orders'),
        )
