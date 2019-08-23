# -*- coding: utf-8 -*-

import logging
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.events.models import AttendanceEvent, Attendee
from apps.marks.models import Suspension
from apps.payment import status
from apps.payment.constants import (FikenAccount, FikenSaleKind, StripeKey, TransactionType,
                                    VatTypeSale)
from apps.webshop.models import OrderLine

User = settings.AUTH_USER_MODEL

logger = logging.getLogger(__name__)


class Payment(models.Model):

    TYPE_CHOICES = (
        (1, _('Umiddelbar')),
        (2, _('Frist')),
        (3, _('Utsettelse')),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    """Which model the payment is created for. For attendance events this should be attendance_event(påmelding)."""
    object_id = models.PositiveIntegerField()
    """Object id for the model chosen in content_type."""
    content_object = GenericForeignKey()
    """Helper attribute which points to the object select in object_id"""
    stripe_key = models.CharField(
        _('stripe key'),
        max_length=10,
        choices=StripeKey.ALL_CHOICES,
        default=StripeKey.ARRKOM,
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
    delay = models.DurationField(_('utsettelse'), blank=True, null=True,
                                 help_text='Oppgi utsettelse på formatet "dager timer:min:sek"')
    """Duration after user attended which they have to pay."""

    # For logging and history
    added_date = models.DateTimeField(_("opprettet dato"), auto_now=True)
    """Day of payment creation. Automatically set"""
    changed_date = models.DateTimeField(auto_now=True, editable=False)
    """Last changed. Automatically set"""
    last_changed_by = models.ForeignKey(  # Blank and null is temperarly
        User,
        editable=False,
        null=True,
        on_delete=models.CASCADE
    )
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
        if self._is_type(OrderLine):
            order_line: OrderLine = self.content_object
            return f'{order_line.user} - {order_line.payment_description}'
        logging.getLogger(__name__).error(
            f'Trying to get description for payment #{self.pk}, but it\'s not an AttendanceEvent or a '
            f'Webshop OrderLine.'
        )
        return 'No description'

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
        elif self._is_type(OrderLine):
            return settings.EMAIL_PROKOM
        else:
            return settings.DEFAULT_FROM_EMAIL

    def is_user_allowed_to_pay(self, user: User) -> bool:
        """
        In the case of attendance events the user should only be allowed to pay if they are attending
        and has not paid yet.
        """
        if self._is_type(AttendanceEvent):
            event: AttendanceEvent = self.content_object
            is_attending = event.is_attendee(user)
            if is_attending:
                attendee = Attendee.objects.get(user=user, event=event)
                return not attendee.has_paid
            return False

        """
        Payments for Webshop orderlines should only be payable for the owner of the orderline
        """
        if self._is_type(OrderLine):
            order_line: OrderLine = self.content_object
            is_order_line_owner = order_line.user == user
            return is_order_line_owner

        """ There are no rules prohibiting user from paying for other types of payments """
        return True

    def handle_payment(self, user: User):
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

        elif self._is_type(OrderLine):
            order_line: OrderLine = self.content_object
            order_line.paid = True
            order_line.save()

    def handle_refund(self, payment_relation):
        """
        Method for handling refunds.
        For events it deletes the Attendee object.

        :param str host: hostname to include in email
        :param PaymentRelation payment_relation: user payment to refund
        """

        if self._is_type(AttendanceEvent):
            Attendee.objects.get(event=self.content_object,
                                 user=payment_relation.user).delete()

        if self._is_type(OrderLine):
            order_line: OrderLine = self.content_object
            order_line.paid = False
            order_line.save()

    def check_refund(self, payment_relation) -> (bool, str):
        """Method for checking if the payment can be refunded"""
        if self._is_type(AttendanceEvent):
            attendance_event = self.content_object
            if attendance_event.unattend_deadline < timezone.now():
                return False, _("Fristen for å melde seg av har utgått")
            if len(Attendee.objects.filter(event=attendance_event, user=payment_relation.user)) == 0:
                return False, _("Du er ikke påmeldt dette arrangementet.")
            if attendance_event.event.event_start < timezone.now():
                return False, _("Dette arrangementet har allerede startet.")

            return True, ''

        if self._is_type(OrderLine):
            return False, 'Du kan ikke refundere betalinger i Webshop på dette tidspunktet'

        return False, 'Refund checks not implemented'

    def prices(self):
        return self.paymentprice_set.all()

    def price(self):
        # TODO implement group based pricing
        if self.paymentprice_set.count() > 0:
            return self.paymentprice_set.all()[0]
        return None

    @property
    def stripe_private_key(self):
        return settings.STRIPE_PRIVATE_KEYS[self.stripe_key]

    @property
    def stripe_public_key(self):
        return settings.STRIPE_PUBLIC_KEYS[self.stripe_key]

    def _is_type(self, model_type):
        return ContentType.objects.get_for_model(model_type) == self.content_type

    @property
    def transaction_type(self):
        if self._is_type(AttendanceEvent):
            return TransactionType.EVENT
        elif self._is_type(OrderLine):
            return TransactionType.WEB_SHOP
        logging.error(f'Payment {self} is related to unsupported model/content-type')

    def __str__(self):
        return self.description()

    def clean_generic_relation(self):
        if not self._is_type(AttendanceEvent) and not self._is_type(OrderLine):
            raise ValidationError({
                'content_type': _('Denne typen objekter støttes ikke av betalingssystemet for tiden.'),
            })
        else:
            if not self.content_object or not self.content_object.event.is_attendance_event():
                raise ValidationError(_('Dette arrangementet har ikke påmelding.'))

    def clean(self):
        super().clean()
        self.clean_generic_relation()

    class Meta:
        unique_together = ('content_type', 'object_id')

        verbose_name = _("betaling")
        verbose_name_plural = _("betalinger")

        default_permissions = ('add', 'change', 'delete')


class PaymentPrice(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    """Payment object"""
    price = models.IntegerField(_("pris"))
    """Price in NOK"""
    description = models.CharField(max_length=128)
    """Description of price"""

    def __str__(self):
        return self.description + " (" + str(self.price) + "kr)"

    class Meta:
        verbose_name = _("pris")
        verbose_name_plural = _("priser")
        default_permissions = ('add', 'change', 'delete')


class PaymentRelation(models.Model):
    """Payment metadata for user"""

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    """Payment object"""
    payment_price = models.ForeignKey(PaymentPrice, on_delete=models.CASCADE)
    """Price object"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    """User who paid"""
    datetime = models.DateTimeField(auto_now=True)
    """Datetime when payment was created"""
    refunded = models.BooleanField(default=False)
    """Has payment been refunded"""

    unique_id = models.CharField(max_length=128, null=True, blank=True)
    """Unique ID for payment"""
    stripe_id = models.CharField(max_length=128, null=True, blank=True)
    """ID from Stripe payment"""

    status = models.CharField(
        max_length=30,
        null=False,
        choices=status.PAYMENT_STATUS_CHOICES,
        default=status.SUCCEEDED
    )
    """ Status of a Stripe payment """
    payment_intent_secret = models.CharField(max_length=200, null=True, blank=True)
    """ Stripe payment intent secret key for verifying pending transactions/intents """

    def get_timestamp(self):
        return self.datetime

    def get_subject(self):
        return "[Kvittering] " + self.payment.description()

    def get_description(self):
        return self.payment.description()

    def get_items(self):
        items = [{
                    'name': self.payment.description(),
                    'price': self.payment_price.price,
                    'quantity': 1
                 }]
        return items

    def get_from_mail(self):
        return settings.EMAIL_ARRKOM

    def get_to_mail(self):
        return self.user.email

    def refund(self):
        self.status = status.REFUNDED
        self.save()

    @property
    def is_refundable(self) -> bool:
        can_refund, reason = self.payment.check_refund(self)
        return can_refund

    @property
    def is_refundable_reason(self) -> str:
        can_refund, reason = self.payment.check_refund(self)
        return reason

    def _create_fiken_sale(self, amount: float):
        FikenSale.objects.create(
            stripe_key=self.payment.stripe_key,
            original_amount=amount,
            transaction_type=self.transaction_type,
            description=f'{self.get_description()} - {self.user.get_full_name()}',
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(self)
        )

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = str(uuid.uuid4())
        super(PaymentRelation, self).save(*args, **kwargs)
        receipt = PaymentReceipt(object_id=self.id,
                                 content_type=ContentType.objects.get_for_model(self))
        receipt.save()

    def __str__(self):
        return self.payment.description() + " - " + str(self.user)

    class Meta:
        verbose_name = _("betalingsrelasjon")
        verbose_name_plural = _("betalingsrelasjoner")
        default_permissions = ('add', 'change', 'delete')


class PaymentDelay(models.Model):
    """User specific payment deadline"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    """Payment object"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    """User object"""
    valid_to = models.DateTimeField()
    """Payment deadline"""

    active = models.BooleanField(default=True)
    """Is payment delay active"""

    def __str__(self):
        return self.payment.description() + " - " + str(self.user)

    class Meta:
        unique_together = ('payment', 'user')

        verbose_name = _('betalingsutsettelse')
        verbose_name_plural = _('betalingsutsettelser')

        default_permissions = ('add', 'change', 'delete')


class PaymentTransaction(models.Model):
    """Transaction for a user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    """User object"""
    amount = models.IntegerField(null=True, blank=True)
    """Amount in NOK"""
    used_stripe = models.BooleanField(default=False)
    """Was transaction paid for using Stripe"""
    datetime = models.DateTimeField(auto_now=True)
    """Transaction creation datetime. Automatically generated."""
    status = models.CharField(
        max_length=30,
        null=False,
        choices=status.PAYMENT_STATUS_CHOICES,
        default=status.SUCCEEDED
    )
    """ Status of a Stripe payment """
    stripe_id = models.CharField(max_length=128, null=True, blank=True)
    """ID from Stripe payment"""
    payment_intent_secret = models.CharField(max_length=200, null=True, blank=True)
    """ Stripe payment intent secret key for verifying pending transactions/intents """

    def get_timestamp(self):
        return self.datetime

    def get_subject(self):
        return "[Kvittering] Saldoinnskudd på online.ntnu.no"

    def get_description(self):
        return "saldoinnskudd på online.ntnu.no"

    def get_items(self):
        items = [{
                'name': "Påfyll av saldo",
                'price': self.amount,
                'quantity': 1
            }]
        return items

    def get_from_mail(self):
        return settings.EMAIL_TRIKOM

    def get_to_mail(self):
        return self.user.email

    def __str__(self):
        return str(self.user) + " - " + str(self.amount) + "(" + str(self.datetime) + ")"

    def _create_fiken_sale(self, amount: float):
        FikenSale.objects.create(
            stripe_key=StripeKey.TRIKOM,
            original_amount=amount,
            transaction_type=TransactionType.KIOSK,
            description=f'{self.get_description()} - {self.user.get_full_name()}',
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(self)
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        receipt = PaymentReceipt(object_id=self.id,
                                 content_type=ContentType.objects.get_for_model(self))
        receipt.save()

    class Meta:
        ordering = ['-datetime']
        verbose_name = _('transaksjon')
        verbose_name_plural = _('transaksjoner')
        default_permissions = ('add', 'change', 'delete')


class PaymentReceipt(models.Model):
    """Transaction receipt"""
    receipt_id = models.UUIDField(default=uuid.uuid4)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    """Which model the receipt is created for"""
    object_id = models.PositiveIntegerField(null=True)
    """Object id for the model chosen in content_type"""
    content_object = GenericForeignKey()
    """Helper attribute which points to the object select in object_id"""

    def save(self, *args, **kwargs):
        transaction = self.content_object
        self.timestamp = transaction.get_timestamp()
        self.subject = transaction.get_subject()
        self.description = transaction.get_description()
        self.items = transaction.get_items()
        self.from_mail = transaction.get_from_mail()
        self.to_mail = [transaction.get_to_mail()]

        self._send_receipt(self.timestamp, self.subject, self.description, self.receipt_id,
                           self.items, self.to_mail, self.from_mail)
        super().save(*args, **kwargs)

    def _is_type(self, model_type):
        """Function for comparing content types to differentiate payment types"""
        return ContentType.objects.get_for_model(model_type) == self.content_type

    def _send_receipt(self, payment_date, subject, description, payment_id, items, to_mail, from_mail):
        """Send confirmation email with receipt
        param receipt: object
        """

        # Calculate total item price and ensure correct input to template.
        receipt_items = []
        total_amount = 0
        for item in items:
            receipt_items.append({
                    'amount': item['price'],
                    'description': item['name'],
                    'quantity': item['quantity']
                    })
            total_amount += item['price'] * item['quantity']

        context = {
            'payment_date': payment_date,
            'description': description,
            'payment_id': payment_id,
            'items': receipt_items,
            'total_amount': total_amount,
            'to_mail': to_mail,
            'from_mail': from_mail
        }

        email_message = render_to_string('payment/email/confirmation_mail.txt', context)
        send_mail(subject, email_message, from_mail, to_mail)

    class Meta:
        default_permissions = ('add', 'change', 'delete')


class FikenSale(models.Model):
    stripe_key = models.CharField(
        'Stripe key',
        max_length=20,
        choices=StripeKey.ALL_CHOICES,
    )
    transaction_type = models.CharField(
        'Transaction Type',
        max_length=20,
        choices=TransactionType.ALL_CHOICES,
    )
    original_amount = models.FloatField()
    kind = models.CharField(
        'Fiken Sale kind',
        max_length=20,
        choices=FikenSaleKind.ALL_CHOICES,
        default=FikenSaleKind.CASH_SALE,
    )
    paid = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    """Which model the receipt is created for"""
    object_id = models.PositiveIntegerField(null=True)
    """Object id for the model chosen in content_type"""
    content_object = GenericForeignKey()
    """Helper attribute which points to the object select in object_id"""

    @property
    def identifier(self) -> str:
        return f'{self.transaction_type.upper()}-{self.id}'

    @property
    def date(self):
        return str(self.created_date.date())

    @property
    def account(self) -> str:
        """
        Fiken account related to the Stripe key used for the sale
        """
        if self.stripe_key == StripeKey.ARRKOM:
            return FikenAccount.ARRKOM
        elif self.stripe_key == StripeKey.FAGKOM:
            return FikenAccount.FAGKOM
        elif self.stripe_key == StripeKey.TRIKOM:
            return FikenAccount.TRIKOM
        elif self.stripe_key == StripeKey.PROKOM:
            return FikenAccount.PROKOM
        return FikenAccount.ARRKOM

    @property
    def amount(self) -> float:
        """
        Convert NOK kr amount to NOK øre amount.
        Remove Stripe fee from the amount
        """
        stripe_fee_percentage = 0.024  # 2.4 %
        stripe_fee = 2  # 2 NOK
        return (self.original_amount * (1.0 - stripe_fee_percentage) - stripe_fee) * 100

    @property
    def vat_type(self) -> str:
        if self.transaction_type == TransactionType.KIOSK:
            return VatTypeSale.OUTSIDE
        elif self.transaction_type == TransactionType.EVENT:
            return VatTypeSale.OUTSIDE
        elif self.transaction_type == TransactionType.WEB_SHOP:
            return VatTypeSale.NONE
        return VatTypeSale.NONE

    @property
    def vat_percentage(self) -> float:
        if self.transaction_type in (TransactionType.EVENT, TransactionType.KIOSK):
            return 0.0
        elif self.transaction_type in (TransactionType.WEB_SHOP,):
            return 0.25
        return 0.0

    @property
    def net_amount(self) -> float:
        return self.amount * (1.0 - self.vat_percentage)

    @property
    def vat_amount(self) -> float:
        return self.amount * self.vat_percentage

    @property
    def lines(self):
        """
        Fiken Order Line description
        """
        return [{
            'netPrice': self.net_amount,
            'vat': self.vat_amount,
            'vatType': self.vat_type,
            'account': self.account,
            'description': self.description,
        }]
