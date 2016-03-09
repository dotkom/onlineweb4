from apps.shop.models import Order, OrderLine
from django.contrib import admin


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ('__str__', 'price', 'quantity')


class OrderLineAdmin(admin.ModelAdmin):
    model = OrderLine
    list_display = ('__str__', 'user', 'datetime')


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
