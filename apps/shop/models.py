from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models

from apps.authentication.models import OnlineUser as User

class Order(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    order_line = models.ForeignKey('OrderLine', related_name='orders')
    # Price of product when paid
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # Quantity of products ordered
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def total_price(self):
        return self.content_object.price * self.quantity

    def reduce_stock(self):
    	self.content_object.reduce_stock(self.quantity)

    def __unicode__(self):
        return unicode(self.content_object)


class OrderLine(models.Model):
    user = models.ForeignKey(User, related_name="u")
    datetime = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def count_orders(self):
        return sum((order.quantity for order in self.orders.all()))

    def subtotal(self):
        return sum((order.total_price() for order in self.orders.all()))

    def pay(self):
        if self.paid:
            return
        # Setting price for orders in case product price changes later
        for order in self.orders.all():
            order.price = order.total_price()
            order.save()
            order.reduce_stock()
        self.paid = True
        self.save()

    def __unicode__(self):
    	return unicode(self.pk)
