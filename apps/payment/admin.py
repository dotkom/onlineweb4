# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from reversion.admin import VersionAdmin

from utils.admin import DepositWithdrawalFilter
from apps.payment.models import (Payment, PaymentDelay, PaymentPrice, PaymentRelation,
                                 PaymentTransaction)


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
    list_display = ('__str__', 'stripe_key', 'payment_type')


class PaymentRelationAdmin(VersionAdmin):
    model = PaymentRelation
    list_display = ('__str__', 'refunded')
    exclude = ('stripe_id',)


class PaymentDelayAdmin(VersionAdmin):
    model = PaymentDelay
    list_display = ('__str__', 'valid_to', 'active')


class PaymentTransactionAdmin(VersionAdmin):
    model = PaymentTransaction
    list_display = ('__str__', 'user', 'datetime', 'amount', 'used_stripe')
    list_filter = ('used_stripe', DepositWithdrawalFilter)


admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentRelation, PaymentRelationAdmin)
admin.site.register(PaymentDelay, PaymentDelayAdmin)
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
