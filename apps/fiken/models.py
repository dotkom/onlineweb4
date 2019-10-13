from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.db import models

from apps.authentication.models import OnlineUser as User
from apps.payment import status
from apps.payment.constants import StripeKey, TransactionType

from .constants import FikenSaleKind, FikenStripeAccount, VatTypeSale, vat_percentage
from .pdf_generator import FikenSalePDF


class FikenAccount(models.Model):
    identifier = models.CharField('Identifikator', max_length=64, null=False, blank=False,
                                  help_text='Kodeord som brukes for å referere til kontoen, f.eks "nibble"',)
    name = models.CharField('Navn', max_length=128, unique=True, null=False, blank=False,
                            help_text='Navnet kontoen har i Fiken')
    code = models.CharField('Kontokode', max_length=128, unique=True, null=False, blank=False,
                            help_text='ID-en til kontoen i Fiken')
    created_date = models.DateTimeField('Opprettelsesdato', auto_now_add=True)
    active = models.BooleanField('Aktiv', default=True,
                                 help_text='Om kontoen fortsatt er i aktiv bruk. Sett heller som inaktiv enn å slette')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Konto i Fiken'
        verbose_name_plural = 'Kontoer i Fiken'
        ordering = ('created_date', 'name',)


class FikenCustomer(models.Model):
    user = models.OneToOneField(
        to=User,
        related_name='fiken_customer',
        on_delete=models.DO_NOTHING,
        verbose_name='Bruker',
    )
    fiken_customer_number = models.IntegerField('Kundenummer', null=True, blank=True, unique=True)

    def __str__(self):
        customer_number = self.fiken_customer_number if self.fiken_customer_number else 'Ikke synkronisert'
        return f'{self.user} ({customer_number})'

    class Meta:
        verbose_name = 'Kunde i Fiken'
        verbose_name_plural = 'Kunder i Fiken'
        ordering = ('user', 'fiken_customer_number',)


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
    original_amount = models.IntegerField()
    kind = models.CharField(
        'Fiken Sale kind',
        max_length=20,
        choices=FikenSaleKind.ALL_CHOICES,
        default=FikenSaleKind.EXTERNAL_INVOICE,
    )
    paid = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        null=False,
        choices=status.PAYMENT_STATUS_CHOICES,
    )
    fiken_id = models.IntegerField(null=True, blank=True)
    customer = models.ForeignKey(
        to=FikenCustomer,
        related_name='sales',
        verbose_name='Kunde',
        on_delete=models.DO_NOTHING,
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    """Which model the receipt is created for"""
    object_id = models.PositiveIntegerField(null=True)
    """Object id for the model chosen in content_type"""
    content_object = GenericForeignKey()
    """Helper attribute which points to the object select in object_id"""

    @staticmethod
    def remove_stripe_fee(price: int) -> int:
        stripe_fee_percentage = 0.014  # 1.4 %
        stripe_fee = 180  # 1.8 Kr NOK
        return int(price * (1 - stripe_fee_percentage) - stripe_fee)

    @property
    def identifier(self) -> str:
        if self.status == status.REMOVED:
            return f'REFUND-{self.id}'
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
            return FikenStripeAccount.ARRKOM
        elif self.stripe_key == StripeKey.FAGKOM:
            return FikenStripeAccount.FAGKOM
        elif self.stripe_key == StripeKey.TRIKOM:
            return FikenStripeAccount.TRIKOM
        elif self.stripe_key == StripeKey.PROKOM:
            return FikenStripeAccount.PROKOM
        return FikenStripeAccount.ARRKOM

    @property
    def amount(self) -> float:
        amount = self.remove_stripe_fee(self.original_amount)
        if self.status == status.REMOVED:
            return -amount
        return amount

    @property
    def lines(self):
        return self.order_lines.all()

    def create_attachment(self):
        sale_attachment = FikenSaleAttachment.objects.create(
            sale=self,
            filename=f'sale-attachment-{self.identifier}.pdf',
            comment='',
        )
        attachment_file = FikenSalePDF(self).render_pdf()
        sale_attachment.file.save(sale_attachment.filename, File(attachment_file))
        return sale_attachment

    def __str__(self):
        return self.identifier

    class Meta:
        verbose_name = 'Salg i Fiken'
        verbose_name_plural = 'Salg i Fiken'
        ordering = ('created_date', 'customer',)


class FikenOrderLine(models.Model):
    sale = models.ForeignKey(to=FikenSale, related_name='order_lines', on_delete=models.CASCADE, null=True)
    price = models.IntegerField()
    vat_type = models.CharField(max_length=200, choices=VatTypeSale.ALL_CHOICES)
    description = models.CharField(max_length=200)
    account = models.ForeignKey(
        to=FikenAccount,
        related_name='order_lines',
        verbose_name='Konto i Fiken',
        on_delete=models.DO_NOTHING,
    )

    @property
    def price_without_fee(self) -> int:
        return self.sale.remove_stripe_fee(self.price)

    @property
    def vat_percentage(self) -> float:
        if self.vat_type not in vat_percentage:
            return 0.0
        return vat_percentage[self.vat_type]

    @property
    def net_price(self) -> int:
        net_price = int(self.price_without_fee * (1 - self.vat_percentage))
        if self.sale.status == status.REMOVED:
            return -net_price
        return net_price

    @property
    def vat_price(self) -> int:
        vat_price = int(self.price_without_fee * self.vat_percentage)
        if self.sale.status == status.REMOVED:
            return -vat_price
        return vat_price

    def __str__(self):
        return f'{self.description} ({int(self.price / 100)} kr)'

    class Meta:
        verbose_name = 'Ordrelinje i Fiken'
        verbose_name_plural = 'Ordrelinjer i Fiken'
        ordering = ('sale', 'pk',)


class FikenSaleAttachment(models.Model):
    sale = models.ForeignKey(
        to=FikenSale,
        related_name='attachments',
        on_delete=models.DO_NOTHING,
        verbose_name='Salg',
    )
    filename = models.CharField('Filnavn', max_length=200)
    file = models.FileField('Fil', upload_to=settings.OW4_FIKEN_FILE_ROOT)
    comment = models.CharField('Kommentar', max_length=4000)
    attach_to_sale = models.BooleanField('Koble til salg', default=False)
    attach_to_payment = models.BooleanField('Koble til betaling', default=True)
    created_date = models.DateTimeField('Opprettelsesdato', auto_now_add=True)

    def __str__(self):
        return f'{self.filename} ({self.created_date})'

    class Meta:
        verbose_name = 'Bilag i Fiken'
        verbose_name_plural = 'Bilag i Fiken'
        ordering = ('sale', 'created_date',)
