# -*- coding: utf-8 -*-

import uuid

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from apps.authentication.models import OnlineUser as User
from apps.events.models import Event, Attendee

class Payment(models.Model):

    TYPE_CHOICES = (
        (1, _('Umiddelbar')),
        (2, _('Frist')),
        (3, _('Utsettelse')),
    )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    price = models.IntegerField(_(u"pris"))
    payment_type = models.SmallIntegerField(_('type'), choices=TYPE_CHOICES)

    #Optional fields depending on payment type
    deadline = models.DateTimeField(_(u"frist"), blank=True, null=True)
    active = models.BooleanField(default=True)
    delay = models.SmallIntegerField(_('utsettelse'), blank=True, null=True)

    added_date = models.DateTimeField(_(u"opprettet dato"), auto_now=True)
    changed_date = models.DateTimeField(auto_now=True, editable=False)
    last_changed_by = models.ForeignKey(User, editable=False, null=True) #blank and null is temperarly


    def paid_users(self):
        return [payment_relation.user for payment_relation in self.paymentrelation_set.all()]

    def payment_delays(self):
        return self.paymentdelay_set.filter(active=True)

    def payment_delay_users(self):
        return [payment_delay.user for payment_delay in self.payment_delays()]


    def description(self):
        if ContentType.objects.get_for_model(Event) == self.content_type:
            return self.content_object.title
        else:
            return "payment description not implemented"

    def responsible_mail(self):
        if ContentType.objects.get_for_model(Event) == self.content_type:
            event_type = self.content_object.event_type
            if event_type == 1 or event_type == 4: # Sosialt & Utflukt
                return settings.EMAIL_ARRKOM
            elif event_type == 2: #Bedpres
                return settings.EMAIL_BEDKOM
            elif event_type == 3: #Kurs
                return settings.EMAIL_FAGKOM
            elif event_type == 5: # Ekskursjon
                return settings.EMAIL_EKSKOM
            else:
                return settings.DEFAULT_FROM_EMAIL
        else:
            return settings.DEFAULT_FROM_EMAIL

    def handle_payment(self, user):
        if ContentType.objects.get_for_model(Event) == self.content_type:
            if self.content_object.is_attendance_event():
                attendee = Attendee.objects.filter(event=self.content_object.attendance_event, user=user)

                if attendee:
                    attendee[0].paid = True
                    attendee[0].save()
                else:
                    Attendee.objects.create(event=self.content_object.attendance_event, user=user, paid=True)

    def __unicode__(self):
        return self.description()

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
        return self.payment.description() + " - " + unicode(self.user)

    class Meta:
        verbose_name = _(u"betalingsrelasjon")
        verbose_name_plural = _(u"betalingsrelasjoner")


class PaymentDelay(models.Model):
    payment = models.ForeignKey(Payment)
    user = models.ForeignKey(User)
    valid_to = models.DateTimeField()

    active = models.BooleanField(default=True)

