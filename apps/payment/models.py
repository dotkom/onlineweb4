# -*- coding: utf-8 -*-

import uuid

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
    deadline = models.DateTimeField(_(u"frist"), blank=True, null=True)
    instant_payment = models.BooleanField(_(u"betaling før påmelding"), help_text=_(u"krev betaling før påmelding"), default=False)
    active = models.BooleanField(default=True)

    #title = models.CharField(_(u"tittel"), max_length=60)
    description = models.CharField(_(u"beskrivelse"), help_text=_(u"Dette feltet kreves kun dersom det er mer enn en betaling"), max_length=60, blank=True, null=True)

    added_date = models.DateTimeField(_(u"opprettet dato"), auto_now=True)
    changed_date = models.DateTimeField(auto_now=True, editable=False)
    last_changed_by = models.ForeignKey(User, editable=False, null=True) #blank and null is temperarly


    def paid_users(self):
        return [payment_relation.user for payment_relation in self.paymentrelation_set.all()]


    def content_object_description(self):
        if hasattr(self.content_object, "payment_description"):
            return self.content_object.payment_description()

        return "payment description not implemented"

    def content_object_mail(self):
        if hasattr(self.content_object, "payment_mail"):
            return self.content_object.payment_mail()

        return settings.DEFAULT_FROM_EMAIL

    def content_object_handle_payment(self, user):
        if hasattr(self.content_object, "payment_complete"):
            self.content_object.payment_complete(user)

    class Meta:
        verbose_name = _(u"betaling")
        verbose_name_plural = _(u"betalinger")

class PaymentRelation(models.Model):
    payment = models.ForeignKey(Payment)
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now=True)

    unique_id = models.CharField(max_length=128, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = str(uuid.uuid4())
        super(PaymentRelation, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.payment.content_object_description() + " - " + unicode(self.user)

    class Meta:
        verbose_name = _(u"betalingsrelasjon")
        verbose_name_plural = _(u"betalingsrelasjoner")

