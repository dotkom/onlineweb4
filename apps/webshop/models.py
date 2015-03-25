# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse

from apps.authentication.models import OnlineUser as User
from filebrowser.fields import FileBrowseField


class Product(models.Model):
    category = models.ForeignKey('Category', related_name='products')
    name = models.CharField(max_length=100)
    short = models.CharField(max_length=200)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveSmallIntegerField()

    def get_absolute_url(self):
        return reverse('webshop_product', args=[str(self.id)])

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkter'


class ProductImage(models.Model):
    IMAGE_FOLDER = "images/webshop"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

    product = models.ForeignKey('Product')
    # image = FileBrowseField(
    #     'bilde', max_length=200,
    #     directory=IMAGE_FOLDER, extensions=IMAGE_EXTENSIONS, null=True
    # )
    image = models.ImageField()

    class Meta:
        verbose_name = 'Produktbilde'
        verbose_name_plural = 'Produktbilder'


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('webshop_category', args=[str(self.id)])

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategorier'


class Order(models.Model):
    product = models.ForeignKey('Product')
    order_line = models.ForeignKey('OrderLine', related_name='orders')
    # Price of product when ordered
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Number of products ordered
    number = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Bestilling'
        verbose_name_plural = 'Bestillinger'


class OrderLine(models.Model):
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now_add=True)
