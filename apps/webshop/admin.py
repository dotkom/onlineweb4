from apps.webshop.models import Category, Order, OrderLine, Product, ProductSize
from django.contrib import admin


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    max_num = 20
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeInline]
    prepopulated_fields = {"slug": ("name",)}


class OrderInline(admin.TabularInline):
    model = Order
    extra = 1


class OrderLineAdmin(admin.ModelAdmin):
    model = OrderLine
    inlines = [OrderInline, ]


class OrderAdmin(admin.ModelAdmin):
    model = Order


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
