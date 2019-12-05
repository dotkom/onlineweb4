from django.contrib import admin

from apps.shop.models import Order, OrderLine


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ("__str__", "price", "quantity", "order_line")


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    readonly_fields = ["__str__"]
    fields = ["__str__", "price", "quantity"]


class OrderLineAdmin(admin.ModelAdmin):
    model = OrderLine
    list_display = ("__str__", "user", "datetime", "paid")
    list_filter = ["paid"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__ntnu_username",
    ]

    inlines = [OrderInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
