# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from reversion.admin import VersionAdmin

from apps.payment.models import (FikenOrderLine, FikenSale, FikenSaleAttachment, Payment,
                                 PaymentDelay, PaymentPrice, PaymentReceipt, PaymentRelation,
                                 PaymentTransaction)
from utils.admin import DepositWithdrawalFilter


class PaymentInline(GenericStackedInline):
    model = Payment
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    exclude = ("added_date", "last_changed_date", "last_changed_by")

    # TODO add proper history updates in dashboard
    # def save_model(self, request, obj, form, change):
    #    obj.last_changed_by = request.user
    #    obj.save()


class PaymentPriceInline(admin.StackedInline):
    model = PaymentPrice
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


class PaymentAdmin(VersionAdmin):
    inlines = (PaymentPriceInline, )
    model = Payment
    list_display = ('__str__', 'active', 'payment_type', 'deadline', 'delay', 'stripe_key')
    list_filter = ['active', 'stripe_key', 'payment_type']


class PaymentRelationAdmin(VersionAdmin):
    model = PaymentRelation
    list_display = ('payment', 'user', 'datetime', 'refunded')
    list_filter = ['refunded']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'user__ntnu_username']
    exclude = ('stripe_id',)


class PaymentDelayAdmin(VersionAdmin):
    model = PaymentDelay
    list_display = ('__str__', 'valid_to', 'active')
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'user__ntnu_username']
    list_filter = ['active']


class PaymentReceiptAdmin(admin.ModelAdmin):
    model = PaymentReceipt
    list_display = ('receipt_id',)
    search_fields = ['receipt_id']


class PaymentTransactionAdmin(VersionAdmin):
    model = PaymentTransaction
    list_display = ('__str__', 'user', 'datetime', 'amount', 'used_stripe')
    list_filter = ('used_stripe', DepositWithdrawalFilter)


class FikenSaleAttachmentInlineAdmin(admin.StackedInline):
    model = FikenSaleAttachment
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    fields = (
        'filename', 'file', 'comment', 'attach_to_sale', 'attach_to_payment', 'created',
    )
    readonly_fields = (
        'filename', 'file', 'comment', 'attach_to_sale', 'attach_to_payment', 'created',
    )


class FikenOrderLineInlineAdmin(admin.StackedInline):
    model = FikenOrderLine
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    fields = (
        'price', 'vat_type', 'description', 'price_without_fee', 'net_price', 'vat_price', 'vat_percentage',
        'account_type',
    )
    readonly_fields = (
        'price', 'vat_type', 'description', 'price_without_fee', 'net_price', 'vat_price', 'vat_percentage',
        'account_type',
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


admin.site.register(PaymentReceipt, PaymentReceiptAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentRelation, PaymentRelationAdmin)
admin.site.register(PaymentDelay, PaymentDelayAdmin)
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
