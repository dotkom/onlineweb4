from django.contrib import admin
from django.conf import settings
from apps.inventory.models import Item

class ItemAdmin(admin.ModelAdmin):
    model = Item
    list_display = ["name","amount","expiration_date"]

admin.site.register(Item, ItemAdmin)