# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from rest_framework.exceptions import NotAcceptable

from apps.events.models import AttendanceEvent, Attendee
from apps.marks.models import Suspension

User = settings.AUTH_USER_MODEL


class Payment(models.Model):

    TYPE_CHOICES = (
        (1, _('Umiddelbar')),
        (2, _('Frist')),
        (3, _('Utsettelse')),
    )

    # Make sure these exist in settings if they are to be used.
    STRIPE_KEY_CHOICES = (
        ('arrkom', 'arrkom'),
        ('prokom', 'prokom'),
        ('trikom', 'trikom'),
        ('fagkom', 'fagkom'),
    )

    content_type = models.ForeignKey(ContentType)
    """Which model the payment is created for. For attendance events this should be event."""
    object_id = models.PositiveIntegerField()
    """Object id for the model chosen in content_type."""
    content_object = GenericForeignKey()
    """Helper attribute which points to the object select in object_id"""
    stripe_key = models.CharField(
        _('stripe key'),
        max_length=10,
        choices=STRIPE_KEY_CHOICES,
        default="arrkom"
    )
    """Which Stripe key to use for payments"""

    payment_type = models.SmallIntegerField(_('type'), choices=TYPE_CHOICES)
    """
        Which payment type to use for payments.
        Can be one of the following:

        - Immediate
        - Deadline. See :attr:`deadline`
        - Delay. See :attr:`delay`
    """

    deadline = models.DateTimeField(_("frist"), blank=True, null=True)
    """Shared deadline for all payments"""
    active = models.BooleanField(default=True)
    """Is payment activated"""
    delay = models.SmallIntegerField(_('utsettelse'), blank=True, null=True, default=2)
    """Number of days after user attended which they have to pay."""

    # For logging and history
    added_date = models.DateTimeField(_("opprettet dato"), auto_now=True)
    """Day of payment creation. Automatically set"""
    changed_date = models.DateTimeField(auto_now=True, editable=False)
    """Last changed. Automatically set"""
    last_changed_by = models.ForeignKey(User, editable=False, null=True)  # Blank and null is temperarly
    """User who last changed payment. Automatically set"""

    def payment_delays(self):
        return self.paymentdelay_set.filter(active=True)

    def payment_delay_users(self):
        return [payment_delay.user for payment_delay in self.payment_delays()]

    def create_payment_delay(self, user, deadline):
        """
        Method for creating a payment delay for user with a set deadline.
        If a PaymentDelay already exsists it is updated with new deadline.

        :param OnlineUser user: User to create payment delay for
        :param datetime.datetime deadline: Payment delay deadline
        """
        payment_delays = self.paymentdelay_set.filter(payment=self, user=user)

        if payment_delays:
            for payment_delay in payment_delays:
                payment_delay.valid_to = deadline
                payment_delay.save()
        else:
            PaymentDelay.objects.create(payment=self, user=user, valid_to=deadline)

    def description(self):
        if self._is_type(AttendanceEvent):
            return self.content_object.event.title

    def get_receipt_description(self):
        receipt_description = ""
        description = [' '] * 30
        temp = self.description()[0:25]
        description[0:len(temp)+1] = list(temp)
        for c in description:
            receipt_description += c
        return receipt_description

    def responsible_mail(self):
        if self._is_type(AttendanceEvent):
            event_type = self.content_object.event.event_type
            if event_type == 1 or event_type == 4:  # Sosialt & Utflukt
                return settings.EMAIL_ARRKOM
            elif event_type == 2:  # Bedpres
                return settings.EMAIL_BEDKOM
            elif event_type == 3:  # Kurs
                return settings.EMAIL_FAGKOM
            elif event_type == 5:  # Ekskursjon
                return settings.EMAIL_EKSKOM
            else:
                return settings.DEFAULT_FROM_EMAIL
        else:
            return settings.DEFAULT_FROM_EMAIL

    def handle_payment(self, user):
        """
        Method for handling payments from user.
        Deletes any relevant payment delays, suspensions and marks user's attendee object as paid.

        :param OnlineUser user: User who paid

        """
        if self._is_type(AttendanceEvent):
            attendee = Attendee.objects.filter(event=self.content_object, user=user)

            # Delete payment delay objects for the user if there are any
            delays = PaymentDelay.objects.filter(payment=self, user=user)
            for delay in delays:
                delay.delete()

            # If the user is suspended because of a lack of payment the suspension is deactivated.
            suspensions = Suspension.objects.filter(payment_id=self.id, user=user)
            for suspension in suspensions:
                suspension.active = False
                suspension.save()

            if attendee:
                attendee[0].paid = True
                attendee[0].save()
            else:
                Attendee.objects.create(event=self.content_object, user=user, paid=True)

    def handle_refund(self, payment_relation):
        """
        Method for handling refunds.
        For events it deletes the Attendee object.

        :param str host: hostname to include in email
        :param PaymentRelation payment_relation: user payment to refund
        """
        payment_relation.refunded = True
        payment_relation.save()

        if self._is_type(AttendanceEvent):
            Attendee.objects.get(event=self.content_object,
                                 user=payment_relation.user).delete()

    def check_refund(self, payment_relation):
        """Method for checking if the payment can be refunded"""
        if self._is_type(AttendanceEvent):
            attendance_event = self.content_object
            if attendance_event.unattend_deadline < timezone.now():
                return False, _("Fristen for og melde seg av har utgått")
            if len(Attendee.objects.filter(event=attendance_event, user=payment_relation.user)) == 0:
                return False, _("Du er ikke påmeldt dette arrangementet.")
            if attendance_event.event.event_start < timezone.now():
                return False, _("Dette arrangementet har allerede startet.")

            return True, ''

        return False, 'Refund checks not implemented'

    def prices(self):
        return self.paymentprice_set.all()

    def price(self):
        # TODO implement group based pricing
        if self.paymentprice_set.count() > 0:
            return self.paymentprice_set.all()[0]
        return None

    def _is_type(self, model_type):
        return ContentType.objects.get_for_model(model_type) == self.content_type

    def __str__(self):
        return self.description()

    class Meta(object):
        unique_together = ('content_type', 'object_id')

        verbose_name = _("betaling")
        verbose_name_plural = _("betalinger")


class PaymentPrice(models.Model):
    payment = models.ForeignKey(Payment)
    """Payment object"""
    price = models.IntegerField(_("pris"))
    """Price in NOK"""
    description = models.CharField(max_length=128, null=True, blank=True)
    """Description of price"""

    def __str__(self):
        if not self.description:
            return str(self.price) + "kr"
        return self.description + " (" + str(self.price) + "kr)"

    class Meta(object):
        verbose_name = _("pris")
        verbose_name_plural = _("priser")


class PaymentRelation(models.Model):
    """Payment metadata for user"""

    payment = models.ForeignKey(Payment)
    """Payment object"""
    payment_price = models.ForeignKey(PaymentPrice)
    """Price object"""
    user = models.ForeignKey(User)
    """User who paid"""
    datetime = models.DateTimeField(auto_now=True)
    """Datetime when payment was created"""
    refunded = models.BooleanField(default=False)
    """Has payment been refunded"""

    unique_id = models.CharField(max_length=128, null=True, blank=True)
    """Unique ID for payment"""
    stripe_id = models.CharField(max_length=128)
    """ID from Stripe payment"""

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = str(uuid.uuid4())
        super(PaymentRelation, self).save(*args, **kwargs)

    def __str__(self):
        return self.payment.description() + " - " + str(self.user)

    class Meta(object):
        verbose_name = _("betalingsrelasjon")
        verbose_name_plural = _("betalingsrelasjoner")


class PaymentDelay(models.Model):
    """User specific payment deadline"""
    payment = models.ForeignKey(Payment)
    """Payment object"""
    user = models.ForeignKey(User)
    """User object"""
    valid_to = models.DateTimeField()
    """Payment deadline"""

    active = models.BooleanField(default=True)
    """Is payment delay active"""

    def __str__(self):
        return self.payment.description() + " - " + str(self.user)

    class Meta(object):
        unique_together = ('payment', 'user')

        verbose_name = _('betalingsutsettelse')
        verbose_name_plural = _('betalingsutsettelser')


class PaymentTransaction(models.Model):
    """Transaction for a user"""
    user = models.ForeignKey(User)
    """User object"""
    amount = models.IntegerField(null=True, blank=True)
    """Amount in NOK"""
    used_stripe = models.BooleanField(default=False)
    """Was transaction paid for using Stripe"""
    datetime = models.DateTimeField(auto_now=True)
    """Transaction creation datetime. Automatically generated."""

    def __str__(self):
        return str(self.user) + " - " + str(self.amount) + "(" + str(self.datetime) + ")"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user.saldo = self.user.saldo + self.amount

            if self.user.saldo < 0:
                raise NotAcceptable("Insufficient funds")

            self.user.save()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-datetime']
        verbose_name = _('transaksjon')
        verbose_name_plural = _('transaksjoner')


class PaymentReceipt(models.Model):
    receipt_id = models.CharField(max_length=128, default=None)
    to_mail = models.EmailField()
    from_mail = models.EmailField()
    subject = models.TextField()
    description = models.TextField()
    transaction_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.receipt_id:
            self.receipt_id = str(uuid.uuid4())
        super().save(*args, **kwargs)


class ReceiptItem(models.Model):
    receipt = models.ForeignKey('PaymentReceipt', related_name='items')
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    quantity = models.IntegerField(default=1)
