# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ModelForm
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
    title = models.CharField(_(u"arrangementstittel"), max_length=50)
    company = models.ForeignKey(Company, related_name=_(u"bedrift"))
    location = models.CharField(_(u"sted"), max_length=50)
    when = models.DateTimeField(_(u'event-start'))
    category = models.IntegerField(_(u"type"), choices=POSTER_TYPES, default=0)
    amount = models.IntegerField(_(u'antall'), blank=True, null=True)
    description = models.TextField(_(u"beskrivelse"), max_length=1000)
    price = models.DecimalField(_(u'pris'), max_digits=10, decimal_places=2, blank=True, null=True)
    display_from = models.DateField(_(u"vis fra"))
    display_to = models.DateField(_(u"vis til"))
    finished = models.BooleanField(_(u"ferdig"), default=False)

    # Order specific
    ordered_date = models.DateTimeField(auto_now_add=True, editable=False)
    ordered_by = models.ForeignKey(User, related_name=_(u"bestilt av"))
    ordered_committee = models.ForeignKey(Group, related_name=_(u'bestilt av komite'))
    assigned_to = models.ForeignKey(User, related_name=_(u'tilordnet til'), blank=True, null=True)
    comments = models.TextField(_(u"kommentar"), max_length=500, blank=True, null=True)
    done = models.BooleanField(_(u"ferdig"), default=False)


    class Meta:
        verbose_name = _(u"plakatbestilling")
        verbose_name_plural = _(u"plakatbestillinger")
        permissions = (
            ('add_poster_order', 'View poster orders'),
            ('overview_poster_order', 'View poster order overview'),
            ('view_poster_order', 'View poster orders'),
        )

    def __str__(self):
        return "Plakat for %(event)s" % {'event': self.title}


class PosterForm(ModelForm):        
    class Meta: 
        model = Poster
