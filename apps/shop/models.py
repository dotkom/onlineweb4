# -*- coding: utf-8 -*-
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotAcceptable

from apps.authentication.models import OnlineUser as User
from apps.inventory.models import Item
from apps.payment.models import PaymentTransaction
from apps.payment.transaction_constants import TransactionSource


class Order(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    order_line = models.ForeignKey(
        "OrderLine", related_name="orders", on_delete=models.CASCADE
    )
    # Price of product when paid
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # Quantity of products ordered
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def total_price(self):
        return self.content_object.price * self.quantity

    def reduce_stock(self):
        self.content_object.reduce_stock(self.quantity)

    def __str__(self):
        return str(self.content_object)

    class Meta:
        default_permissions = ("add", "change", "delete")


class OrderLine(models.Model):
    user = models.ForeignKey(
        to=User,
        related_name="shop_order_lines",
        on_delete=models.CASCADE,
        verbose_name=_("Bruker"),
    )
    datetime = models.DateTimeField(auto_now_add=True, verbose_name=_("Tidspunkt"))
    paid = models.BooleanField(default=False, verbose_name=_("Betalt"))
    transaction = models.OneToOneField(
        to=PaymentTransaction,
        verbose_name=_("Transaksjon"),
        related_name="shop_order_line",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def count_orders(self):
        return sum((order.quantity for order in self.orders.all()))

    def subtotal(self):
        return sum((order.total_price() for order in self.orders.all()))

    def get_order_descriptions(self):
        descriptions = []
        for order in self.orders.all():
            item: Item = order.content_object
            descriptions.append(
                {"name": item.name, "price": item.price, "quantity": order.quantity}
            )
        return descriptions

    def pay(self):
        if self.paid:
            return

        subtotal = self.subtotal()
        user_wallet = PaymentTransaction.objects.aggregate_coins(self.user)

        if subtotal > user_wallet:
            self.delete()
            raise NotAcceptable("Insufficient funds")

        # Setting price for orders in case product price changes later
        for order in self.orders.all():
            order.price = order.total_price()
            order.save()
            order.reduce_stock()

        # Create the transaction for the user, which will track the actual balance of their wallet
        transaction = PaymentTransaction.objects.create(
            source=TransactionSource.SHOP, amount=-subtotal, user=self.user
        )

        self.transaction = transaction
        self.paid = True
        self.save()

    def clean(self):
        super().clean()
        if not self.orders.exists():
            raise ValidationError("An orderline must contain at least one order")

    def __str__(self):
        return str(self.pk)

    class Meta:
        default_permissions = ("add", "change", "delete")


class MagicToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField("token", default=uuid.uuid4, max_length=36)
    data = models.TextField("data")
    created = models.DateTimeField("created", editable=False, auto_now_add=True)

    class Meta:
        default_permissions = ("add", "change", "delete")
