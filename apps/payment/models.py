# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from apps.authentication.models import OnlineUser as User

class Payment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    price = models.IntegerField(_(u"pris"))
    deadline = models.DateTimeField(_(u"frist"), editable=False)
    instant_payment = models.BooleanField(_(u"betaling for påmelding"))

    added_date = models.DateTimeField(_(u"opprettet dato"))
    changed_date = models.DateTimeField(auto_now=True, editable=False)
    last_changed_by = models.ForeignKey(User, editable=False)

class PaymentRelation(models.Model):
    payment = models.ForeignKey(Payment)
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now=True)