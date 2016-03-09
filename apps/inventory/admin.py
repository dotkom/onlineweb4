from apps.inventory.models import Batch, Item
from django.contrib import admin


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 0


class ItemAdmin(admin.ModelAdmin):
    inlines = [BatchInline]
    model = Item
    list_display = [
        'name',
        'total_amount',
        'oldest_expiration_date',
        'last_added'
    ]

admin.site.register(Item, ItemAdmin)
