from django.contrib import admin

from django.contrib import admin
from django.contrib.contenttypes import generic

from apps.payment.models import Payment
from apps.payment.models import PaymentRelation


class PaymentInline(generic.GenericStackedInline):
    model = Payment
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    exclude = ("added_date", "last_changed_date", "last_changed_by")

    #def save_model(self, request, obj, form, change):
    #    obj.last_changed_by = request.user
    #    obj.save()


class PaymentAdmin(admin.ModelAdmin):
    model = Payment

#TODO remove paymentRelation in prod

class PaymentRelationAdmin(admin.ModelAdmin):
    model = PaymentRelation
    


admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentRelation, PaymentRelationAdmin)
