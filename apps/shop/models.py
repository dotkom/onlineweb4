# -*- coding: utf-8 -*-
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.exceptions import NotAcceptable

from apps.authentication.models import OnlineUser as User


class Order(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    order_line = models.ForeignKey('OrderLine', related_name='orders', on_delete=models.CASCADE)
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
        default_permissions = ('add', 'change', 'delete')


class OrderLine(models.Model):
    user = models.ForeignKey(User, related_name="u", on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def count_orders(self):
        return sum((order.quantity for order in self.orders.all()))

    def subtotal(self):
        return sum((order.total_price() for order in self.orders.all()))

    def pay(self):
        if self.paid:
            return

        if self.subtotal() > self.user.saldo:
            self.delete()
            raise NotAcceptable("Insufficient funds")

        # Setting price for orders in case product price changes later
        for order in self.orders.all():
            order.price = order.total_price()
            order.save()
            order.reduce_stock()

        self.user.saldo = self.user.saldo - self.subtotal()
        self.user.save()

        self.paid = True
        self.save()

    def __str__(self):
        return str(self.pk)

    class Meta:
        default_permissions = ('add', 'change', 'delete')


class MagicToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField('token', default=uuid.uuid4, max_length=36)
    data = models.TextField('data')
    created = models.DateTimeField('created', editable=False, auto_now_add=True)

    class Meta:
        default_permissions = ('add', 'change', 'delete')
