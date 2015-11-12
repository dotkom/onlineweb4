# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage


class Product(models.Model):
    category = models.ForeignKey('Category', related_name='products')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    short = models.CharField(max_length=200)
    description = models.TextField()
    images_csv = models.CommaSeparatedIntegerField(max_length=200, default=None, blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveSmallIntegerField(null=True, blank=True)

    deadline = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('webshop_product', args=[str(self.slug)])

    def related_products(self):
        return self.category.products.exclude(id=self.id)

    @property
    def images(self):
        if self.images_csv:
            id_tuple = self.images_csv.split(',')
            return ResponsiveImage.objects.filter(id__in=id_tuple)
        return ResponsiveImage.objects.none()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkter'


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('webshop_category', args=[str(self.slug)])

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategorier'


class ProductSize(models.Model):
    product = models.ForeignKey(Product)
    size = models.CharField(u'Størrelse', max_length=25)
    description = models.CharField(u'Beskrivelse', max_length=50, null=True, blank=True)
    stock = models.PositiveSmallIntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.size

    class Meta:
        verbose_name = 'Størrelse'
        verbose_name_plural = 'Størrelser'


class Order(models.Model):
    product = models.ForeignKey('Product')
    order_line = models.ForeignKey('OrderLine', related_name='orders')
    # Price of product when paid
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # Quantity of products ordered
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    size = models.ForeignKey(ProductSize, null=True, blank=True)

    def calculate_price(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return u"%sx %s" % (self.quantity, self.product)

    class Meta:
        verbose_name = 'Bestilling'
        verbose_name_plural = 'Bestillinger'


class OrderLine(models.Model):
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=50, null=True, blank=True)

    def count_orders(self):
        return sum((order.quantity for order in self.orders.all()))

    def subtotal(self):
        return sum((order.calculate_price() for order in self.orders.all()))

    def pay(self):
        if self.paid:
            return
        # Setting price for orders in case product price changes later
        for order in self.orders.all():
            order.price = order.calculate_price()
            order.save()
        self.paid = True
        self.save()

    def __unicode__(self):
        return u"Webshop purchase %s by %s" % (self.datetime, self.user)
