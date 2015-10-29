from django.contrib import admin

from apps.shop.models import Order, OrderLine


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ('__unicode__', 'price', 'quantity')



class OrderLineAdmin(admin.ModelAdmin):
    model = OrderLine
    list_display = ('__unicode__', 'user', 'datetime')


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
