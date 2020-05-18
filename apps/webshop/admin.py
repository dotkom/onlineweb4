from django.contrib import admin

from apps.webshop.models import Category, Order, OrderLine, Product, ProductSize


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    max_num = 20
    extra = 0
    classes = ("grp-collapse grp-open",)  # style
    inline_classes = ("grp-collapse grp-open",)  # style


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ["name", "category", "active", "price", "stock"]
    list_filter = ["active", "category"]
    search_fields = ["name"]

    inlines = [ProductSizeInline]
    prepopulated_fields = {"slug": ("name",)}


class OrderInline(admin.TabularInline):
    model = Order
    extra = 1


class OrderLineAdmin(admin.ModelAdmin):
    model = OrderLine

    list_display = ["user", "datetime", "paid", "delivered"]
    list_filter = ["paid", "delivered"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__ntnu_username",
    ]

    inlines = [OrderInline]


class OrderAdmin(admin.ModelAdmin):
    model = Order

    list_display = ["product", "price", "quantity", "size"]
    list_filter = ["product"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
