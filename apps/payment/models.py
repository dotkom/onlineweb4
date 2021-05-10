# -*- coding: utf-8 -*-

import logging
import uuid
from typing import List

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.marks.models import Suspension
from apps.notifications.constants import PermissionType
from apps.notifications.utils import send_message_to_users
from apps.payment import status

from .mixins import PaymentMixin, ReceiptMixin
from .transaction_constants import TransactionSource

User = settings.AUTH_USER_MODEL

logger = logging.getLogger(__name__)


class Payment(models.Model):

    TYPE_CHOICES = ((1, _("Umiddelbar")), (2, _("Frist")), (3, _("Utsettelse")))

    # Make sure these exist in settings if they are to be used.
    STRIPE_KEY_CHOICES = (
        ("arrkom", "arrkom"),
        ("prokom", "prokom"),
        ("trikom", "trikom"),
        ("fagkom", "fagkom"),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    """Which model the payment is created for. For attendance events this should be attendance_event(påmelding)."""
    object_id = models.PositiveIntegerField()
    """Object id for the model chosen in content_type."""
    content_object: PaymentMixin = GenericForeignKey()
    """Helper attribute which points to the object select in object_id"""
    stripe_key = models.CharField(
        _("stripe key"), max_length=10, choices=STRIPE_KEY_CHOICES, default="arrkom"
    )
    """Which Stripe key to use for payments"""

    payment_type = models.SmallIntegerField(_("type"), choices=TYPE_CHOICES)
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
    delay = models.DurationField(
        _("utsettelse"),
        blank=True,
        null=True,
        help_text='Oppgi utsettelse på formatet "dager timer:min:sek"',
    )
    """Duration after user attended which they have to pay."""

    # For logging and history
    added_date = models.DateTimeField(_("opprettet dato"), auto_now=True)
    """Day of payment creation. Automatically set"""
    changed_date = models.DateTimeField(auto_now=True, editable=False)
    """Last changed. Automatically set"""
    last_changed_by = models.ForeignKey(  # Blank and null is temperarly
        User, editable=False, null=True, on_delete=models.CASCADE
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
        return self.content_object.get_payment_description()

    def get_receipt_description(self):
        receipt_description = ""
        description = [" "] * 30
        temp = self.description()[0:25]
        description[0 : len(temp) + 1] = list(temp)
        for c in description:
            receipt_description += c
        return receipt_description

    def responsible_mail(self):
        return self.content_object.get_payment_email()

    def is_user_allowed_to_pay(self, user: User) -> bool:
        return self.content_object.is_user_allowed_to_pay(user)

    def handle_payment(self, user: User):
        """
        Method for handling payments from user.
        Deletes any relevant payment delays, suspensions and marks user's attendee object as paid.

        :param OnlineUser user: User who paid
        """
        # Delete payment delay objects for the user if there are any
        delays = PaymentDelay.objects.filter(payment=self, user=user)
        for delay in delays:
            delay.delete()

        # If the user is suspended because of a lack of payment the suspension is deactivated.
        suspensions = Suspension.objects.filter(payment_id=self.id, user=user)
        for suspension in suspensions:
            suspension.active = False
            suspension.save()

        self.content_object.on_payment_done(user)

    def handle_refund(self, payment_relation):
        self.content_object.on_payment_refunded(payment_relation)

    def check_refund(self, payment_relation) -> (bool, str):
        return self.content_object.can_refund_payment(payment_relation)

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

    def __str__(self):
        return self.description()

    def clean_generic_relation(self):
        if not isinstance(self.content_object, PaymentMixin):
            raise ValidationError(
                {
                    "content_type": _(
                        "Denne typen objekter støttes ikke av betalingssystemet for tiden."
                    )
                }
            )

    def clean(self):
        super().clean()
        self.clean_generic_relation()

    class Meta:
        unique_together = ("content_type", "object_id")

        verbose_name = _("betaling")
        verbose_name_plural = _("betalinger")

        default_permissions = ("add", "change", "delete")


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
        default_permissions = ("add", "change", "delete")
        ordering = ("payment", "price")


class StripeMixin(models.Model):
    status = models.CharField(
        max_length=30,
        null=False,
        choices=status.PAYMENT_STATUS_CHOICES,
        default=status.SUCCEEDED,
    )
    create_receipt = models.BooleanField(
        _("Lag kvittering"),
        default=True,
        help_text="Skal det sendes en kvittering for kjøpet?",
    )
    stripe_id = models.CharField(max_length=128, null=True, blank=True)
    payment_intent_secret = models.CharField(max_length=200, null=True, blank=True)
    """ Stripe payment intent secret key for verifying pending transactions/intents """

    class Meta:
        abstract = True


class PaymentRelation(ReceiptMixin, StripeMixin, models.Model):
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

    def get_receipt_timestamp(self) -> timezone.datetime:
        return self.datetime

    def get_receipt_subject(self) -> str:
        return "[Kvittering] " + self.payment.description()

    def get_receipt_description(self) -> str:
        return self.payment.description()

    def get_receipt_items(self) -> List[dict]:
        return self.payment.content_object.get_payment_receipt_items(self)

    def get_receipt_from_email(self) -> str:
        return self.payment.responsible_mail()

    def get_receipt_to_user(self) -> User:
        return self.user

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

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = str(uuid.uuid4())
        super(PaymentRelation, self).save(*args, **kwargs)

    def __str__(self):
        return self.payment.description() + " - " + str(self.user)

    class Meta:
        verbose_name = _("betalingsrelasjon")
        verbose_name_plural = _("betalingsrelasjoner")
        default_permissions = ("add", "change", "delete")
        ordering = ("datetime", "unique_id")


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
        unique_together = ("payment", "user")
        verbose_name = _("betalingsutsettelse")
        verbose_name_plural = _("betalingsutsettelser")
        default_permissions = ("add", "change", "delete")
        ordering = ("active", "valid_to")


class TransactionManager(models.Manager):
    def aggregate_coins(self, user: User) -> int:
        """
        :return: The aggregated amount of coins in a users wallet.
        """
        value = (
            self.filter(user=user, status=status.DONE)
            .aggregate(coins=models.Sum("amount"))
            .get("coins")
        )
        return value if value is not None else 0


class PaymentTransaction(ReceiptMixin, StripeMixin, models.Model):
    """
    A transaction for a User
    The set of all transactions for a user defines the amount of 'coins' a user has.
    """

    objects = TransactionManager()

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
    """Amount in NOK"""
    source = models.CharField(max_length=64, choices=TransactionSource.ALL_CHOICES)
    """ Origin of the transaction, such as purchases in Nibble or additions from Stripe """
    datetime = models.DateTimeField(auto_now_add=True)

    @property
    def used_stripe(self):
        return self.source == TransactionSource.STRIPE

    def get_receipt_timestamp(self) -> timezone.datetime:
        return self.datetime

    def get_receipt_subject(self) -> str:
        return f"[Kvittering] {self.get_receipt_description()}"

    def get_receipt_description(self) -> str:
        if self.source == TransactionSource.STRIPE:
            return "Saldoinnskudd på online.ntnu.no"
        elif self.source == TransactionSource.TRANSFER:
            return "Overføring av saldo til annen bruker på online.ntnu.no"
        elif self.source == TransactionSource.CASH:
            return "Innskudd av kontanter på online.ntnu.no"
        elif self.source == TransactionSource.SHOP:
            return "Kjøp i Onlinekiosken"

    def get_receipt_items(self):
        if self.source == TransactionSource.STRIPE:
            return [{"name": "Påfyll av saldo", "price": self.amount, "quantity": 1}]
        elif self.source == TransactionSource.TRANSFER:
            return [
                {"name": "Overføring av saldo", "price": self.amount, "quantity": 1}
            ]
        elif self.source == TransactionSource.CASH:
            return [
                {"name": "Påfyll av kontanter", "price": self.amount, "quantity": 1}
            ]
        elif self.source == TransactionSource.SHOP:
            if hasattr(self, "shop_order_line"):
                return self.shop_order_line.get_order_descriptions()
            else:
                raise ValueError(
                    "Transaction for a shop purchase is not connected to an OrderLine"
                )

    def get_receipt_from_email(self):
        return settings.EMAIL_TRIKOM

    def get_receipt_to_user(self):
        return self.user

    def __str__(self):
        return f"{self.user} - {self.amount} ({self.datetime})"

    class Meta:
        ordering = ["-datetime"]
        verbose_name = _("transaksjon")
        verbose_name_plural = _("transaksjoner")
        default_permissions = ("add", "change", "delete")


class PaymentReceipt(models.Model):
    """Transaction receipt"""

    receipt_id = models.UUIDField(default=uuid.uuid4)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    """Which model the receipt is created for"""
    object_id = models.PositiveIntegerField(null=True)
    """Object id for the model chosen in content_type"""
    content_object: ReceiptMixin = GenericForeignKey()
    """Helper attribute which points to the object select in object_id"""

    def save(self, *args, **kwargs):
        paying_user = self.content_object.get_receipt_to_user()
        self._send_receipt(
            payment_id=self.receipt_id,
            payment_date=self.content_object.get_receipt_timestamp(),
            subject=self.content_object.get_receipt_subject(),
            description=self.content_object.get_receipt_description(),
            items=self.content_object.get_receipt_items(),
            from_mail=self.content_object.get_receipt_from_email(),
            to_users=[paying_user],
        )
        super().save(*args, **kwargs)

    def _send_receipt(
        self,
        payment_date: timezone.datetime,
        subject: str,
        description: str,
        payment_id: str,
        items: List[dict],
        to_users: List[User],
        from_mail: str,
    ):
        """Send confirmation email with receipt"""

        # Calculate total item price and ensure correct input to template.
        receipt_items = []
        total_amount = 0
        for item in items:
            receipt_items.append(
                {
                    "amount": item["price"],
                    "description": item["name"],
                    "quantity": item["quantity"],
                }
            )
            total_amount += item["price"] * item["quantity"]

        context = {
            "payment_date": payment_date,
            "description": description,
            "payment_id": payment_id,
            "items": receipt_items,
            "total_amount": total_amount,
            "to_mail": [user.primary_email for user in to_users],
            "from_mail": from_mail,
        }

        message = render_to_string("payment/email/confirmation_mail.txt", context)
        send_message_to_users(
            title=subject,
            content=message,
            recipients=to_users,
            from_email=from_mail,
            permission_type=PermissionType.RECEIPT,
        )

    class Meta:
        default_permissions = ("add", "change", "delete")
