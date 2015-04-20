# -*- coding: utf-8 -*-

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from apps.authentication.models import OnlineUser as User
from apps.events.models import AttendanceEvent, Attendee

class Payment(models.Model):

    TYPE_CHOICES = (
        (1, _(u'Umiddelbar')),
        (2, _(u'Frist')),
        (3, _(u'Utsettelse')),
    )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    price = models.IntegerField(_(u"pris"))
    payment_type = models.SmallIntegerField(_(u'type'), choices=TYPE_CHOICES)

    #Optional fields depending on payment type
    deadline = models.DateTimeField(_(u"frist"), blank=True, null=True)
    active = models.BooleanField(default=True)
    delay = models.SmallIntegerField(_(u'utsettelse'), blank=True, null=True, default=2)

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
        if ContentType.objects.get_for_model(AttendanceEvent) == self.content_type:
            return self.content_object.event.title
        else:
            return "payment description not implemented"

    def responsible_mail(self):
        if ContentType.objects.get_for_model(AttendanceEvent) == self.content_type:
            event_type = self.content_object.event.event_type
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
        if ContentType.objects.get_for_model(AttendanceEvent) == self.content_type:
            attendee = Attendee.objects.filter(event=self.content_object, user=user)

            # Delete payment delay objects for the user if there are any
            delays = PaymentDelay.objects.filter(payment=self, user=user)
            for delay in delays:
                delay.delete()

            if attendee:
                attendee[0].paid = True
                attendee[0].save()
            else:
                Attendee.objects.create(event=self.content_object, user=user, paid=True)

    def handle_refund(self, host, payment_relation):
        if ContentType.objects.get_for_model(AttendanceEvent) == self.content_type:
            self.content_object.notify_waiting_list(
                host=host, unattended_user=payment_relation.user)
            Attendee.objects.get(event=self.content_object, 
                user=payment_relation.user).delete()


    def check_refund(self, payment_relation):
        if ContentType.objects.get_for_model(AttendanceEvent) == self.content_type:
            attendance_event = self.content_object
            user = payment_relation.user
            if attendance_event.unattend_deadline < timezone.now():
                return (False, _(u"Fristen for og melde seg av har utgått"))
            if len(Attendee.objects.filter(event=attendance_event, user=user)) == 0:
                return (False, _(u"Du er ikke påmeldt dette arrangementet."))
            if attendance_event.event.event_start < timezone.now():
                return (False, _(u"Dette arrangementet har allerede startet."))

            return (True, '')
            

    def __unicode__(self):
        return self.description()

    class Meta:
        verbose_name = _(u"betaling")
        verbose_name_plural = _(u"betalinger")

class PaymentRelation(models.Model):
    payment = models.ForeignKey(Payment)
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now=True)
    refunded = models.BooleanField(default=False)

    unique_id = models.CharField(max_length=128, null=True, blank=True)
    stripe_id = models.CharField(max_length=128)

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

    def __unicode__(self):
        return self.payment.description() + " - " + unicode(self.user)

