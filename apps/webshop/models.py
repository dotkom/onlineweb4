# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, validate_comma_separated_integer_list
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.authentication.models import OnlineUser as User
from apps.fiken.constants import VatTypeSale
from apps.fiken.models import FikenAccount
from apps.gallery.models import ResponsiveImage


class Product(models.Model):
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    short = models.CharField(max_length=200)
    description = models.TextField()
    images_csv = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=200,
        default=None,
        blank=True,
        null=True,
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Antall på lager. Blankt vil si uendelig."
    )

    deadline = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    vat_type = models.CharField('Momstype', max_length=200, choices=VatTypeSale.ALL_CHOICES, default=VatTypeSale.NONE)
    fiken_account = models.ForeignKey(
        to=FikenAccount,
        related_name='products',
        verbose_name='Konto i Fiken',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=False,
    )

    def calculate_stock(self):
        """Calculates amount of stock based on either product sizes or product stock

        Returns:
            int: Stock amount. None if stock isn't used
        """
        if self.product_sizes.count() > 0:
            sizes = self.product_sizes.all()
            sizes_with_stock = [size for size in sizes if size.stock is not None]
            if len(sizes_with_stock) != len(sizes):
                # One of the sizes is unlimited(None) which means stock size isn't relevant
                return None
            return sum(product_size.stock for product_size in sizes_with_stock)
        else:
            return self.stock

    def in_stock(self):
        """Check if product is in stock

        Returns:
            bool: product in stock
        """
        stock = self.calculate_stock()
        return stock is None or stock > 0

    def enough_stock(self, quantity, product_size=None):
        """Calculate if there are enough products for a purchase

        Args:
            quantity (int): Quantity to buy
            product_size (ProductSize, optional): product size that is bought

        Returns:
            bool: has enough stock
        """
        stock = self.stock
        if product_size:
            stock = product_size.stock
        return stock is None or stock >= quantity

    def get_absolute_url(self):
        return reverse('webshop_product', args=[str(self.slug)])

    def related_products(self):
        """Products in same category excluding this product

        Returns:
            QuerySet: QuerySet of products
        """
        return self.category.products.exclude(id=self.id)

    @property
    def images(self):
        """Hacky way to support multiple images for a product

        Uses the images_cvs field to lookup ResponsiveImage objects

        Returns:
            QuerySet: QuerySet of images
        """
        if self.images_csv:
            id_tuple = self.images_csv.split(',')
            return ResponsiveImage.objects.filter(id__in=id_tuple)
        return ResponsiveImage.objects.none()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkter'
        permissions = (
            ('view_product', 'View Product'),
        )
        default_permissions = ('add', 'change', 'delete')


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('webshop_category', args=[str(self.slug)])

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategorier'
        permissions = (
            ('view_category', 'View Category'),
        )
        default_permissions = ('add', 'change', 'delete')


class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name='product_sizes', on_delete=models.CASCADE)
    size = models.CharField('Størrelse', max_length=25)
    description = models.CharField('Beskrivelse', max_length=50, null=True, blank=True)
    stock = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Antall på lager. Blankt vil si uendelig."
    )

    def __str__(self):
        if self.description:
            return "%s - %s" % (self.size, self.description)
        return self.size

    class Meta:
        verbose_name = 'Størrelse'
        verbose_name_plural = 'Størrelser'
        default_permissions = ('add', 'change', 'delete')


class Order(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    order_line = models.ForeignKey('OrderLine', related_name='orders', on_delete=models.CASCADE)
    # Price of product when paid
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # Quantity of products ordered
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    size = models.ForeignKey(ProductSize, null=True, blank=True, on_delete=models.CASCADE)

    def is_valid(self):
        """Validate order

        Returns:
            bool: valid order
        """
        return self.product.enough_stock(self.quantity, self.size)

    def calculate_price(self):
        """Calculate total price based on price per product and quantity

        Returns:
            int: price
        """
        return self.product.price * self.quantity

    def __str__(self):
        if self.size:
            return "%sx %s (%s)" % (self.quantity, self.product, self.size.size)
        return "%sx %s" % (self.quantity, self.product)

    class Meta:
        verbose_name = 'Bestilling'
        verbose_name_plural = 'Bestillinger'
        permissions = (
            ('view_order', 'View Order'),
        )
        default_permissions = ('add', 'change', 'delete')


class OrderLine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=50, null=True, blank=True)
    delivered = models.BooleanField(default=False)
    payments = GenericRelation('payment.Payment')

    @staticmethod
    def get_current_order_line_for_user(user: User):
        """
        Gets the currently active OrderLine for a user
        Users can only have a single OrderLine in progress at a time.
        If it does not exist a new one will be created.

        Returns: OrderLine: the current OrderLine for the user
        """
        if not user.is_authenticated:
            return None

        current_order_line = OrderLine.objects.filter(user=user, paid=False).first()
        if not current_order_line:
            current_order_line = OrderLine.objects.create(user=user)

        return current_order_line

    @property
    def payment(self):
        return self.payments.all().first()

    @property
    def payment_description(self):
        all_orders = self.orders.all()
        order_count = sum(map(lambda order: order.quantity, all_orders))
        return f'{order_count} varer fra Onlines webshop'

    def count_orders(self):
        """Total sum of all products

        Returns:
            int: sum of products
        """
        return sum(order.quantity for order in self.orders.all())

    def subtotal(self):
        """Subtotal of products

        Returns:
            int: subtotal
        """
        return sum(order.calculate_price() for order in self.orders.all())

    def is_valid(self):
        """Check that all orders are valid

        Returns:
            bool: orders are valid
        """
        return all((order.is_valid() for order in self.orders.all()))

    def update_stock(self, order):
        """Updates stock for ProductSize if present or Product

        Args:
            order (Order): Order to update
        """
        if order.size and order.size.stock:
            order.size.stock -= order.quantity
            order.size.save()
        elif order.product.stock:
            order.product.stock -= order.quantity
            order.product.save()

    def pay(self):
        """Marks order as paid, stores current price and updates stock"""
        if self.paid:
            return
        # Setting price for orders in case product price changes later
        for order in self.orders.all():
            self.update_stock(order)
            order.price = order.calculate_price()
            order.save()
        self.paid = True
        self.datetime = timezone.now()
        self.save()
        self.send_receipt()

    def get_timestamp(self):
        return self.datetime

    def get_subject(self):
        return "[Kvittering] Kjøp i webshop på online.ntnu.no"

    def get_description(self):
        return "varer i webshop"

    def get_items(self):
        items = []

        for order in self.orders.all():
            item = {
                'name': order.product.name,
                'price': int(order.price / order.quantity),
                'quantity': order.quantity
            }
            items.append(item)
        return items

    def get_from_mail(self):
        return settings.EMAIL_PROKOM

    def get_to_mail(self):
        return self.user.email

    def send_receipt(self):
        from apps.payment.models import PaymentReceipt  # Import PaymentReceipt to avoid circular dependency.
        receipt = PaymentReceipt(object_id=self.id,
                                 content_type=ContentType.objects.get_for_model(self))
        receipt.save()

    def __str__(self):
        return "Webshop purchase %s by %s" % (self.datetime, self.user)

    class Meta:
        permissions = (
            ('view_order_line', 'View Order Line'),
        )
        default_permissions = ('add', 'change', 'delete')
