from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import FikenCustomer, FikenOrderLine, FikenSale, FikenSaleAttachment


class FikenSaleAttachmentInlineAdmin(admin.StackedInline):
    model = FikenSaleAttachment
    extra = 0
    classes = ('grp-collapse grp-open',)
    fields = (
        'filename', 'file', 'comment', 'attach_to_sale', 'attach_to_payment', 'created_date',
    )
    readonly_fields = (
        'filename', 'file', 'comment', 'attach_to_sale', 'attach_to_payment', 'created_date',
    )


class FikenOrderLineInlineAdmin(admin.StackedInline):
    model = FikenOrderLine
    extra = 0
    classes = ('grp-collapse grp-open',)
    fields = (
        'price', 'vat_type', 'description', 'price_without_fee', 'net_price', 'vat_price', 'vat_percentage',
        'account',
    )
    readonly_fields = (
        'price', 'vat_type', 'description', 'price_without_fee', 'net_price', 'vat_price', 'vat_percentage',
        'account',
    )


@admin.register(FikenSale)
class FikenSaleAdmin(VersionAdmin):
    model = FikenSale
    inlines = (FikenOrderLineInlineAdmin, FikenSaleAttachmentInlineAdmin)
    list_display = ('__str__', 'stripe_key', 'created_date', 'amount', 'original_amount',)
    fields = (
        'stripe_key', 'account', 'amount', 'original_amount', 'date', 'kind', 'paid', 'transaction_type', 'status',
        'fiken_id', 'content_type', 'object_id', 'created_date', 'identifier', 'customer',
    )
    readonly_fields = (
        'stripe_key', 'account', 'amount', 'original_amount', 'date', 'kind', 'paid', 'transaction_type', 'status',
        'fiken_id', 'content_type', 'object_id', 'created_date', 'identifier',
    )


@admin.register(FikenCustomer)
class FikenCustomerAdmin(VersionAdmin):
    model = FikenCustomer
