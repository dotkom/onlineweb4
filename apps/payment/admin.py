from django.contrib import admin

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from apps.payment.models import Payment
from apps.payment.models import PaymentDelay
from apps.payment.models import PaymentPrice
from apps.payment.models import PaymentRelation

from reversion.admin import VersionAdmin


class PaymentInline(GenericStackedInline):
    model = Payment
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    exclude = ("added_date", "last_changed_date", "last_changed_by")

    #TODO add proper history updates in dashboard
    #def save_model(self, request, obj, form, change):
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
    list_display = ('__unicode__', 'stripe_key_index', 'payment_type')

class PaymentRelationAdmin(VersionAdmin):
    model = PaymentRelation
    list_display = ('__unicode__', 'refunded')
    exclude = ('stripe_id',)

class PaymentDelayAdmin(VersionAdmin):
    model = PaymentDelay
    list_display = ('__unicode__', 'valid_to', 'active')

admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentRelation, PaymentRelationAdmin)
admin.site.register(PaymentDelay, PaymentDelayAdmin)
