from django.contrib import admin

from apps.inventory.models import Batch, Item


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 0


class ItemAdmin(admin.ModelAdmin):
    inlines = [BatchInline]
    model = Item
    list_display = [
        'name',
        'category',
        'total_amount',
        'oldest_expiration_date',
        'last_added',
        'available',
        'price',
    ]


admin.site.register(Item, ItemAdmin)
