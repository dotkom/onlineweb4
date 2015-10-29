from rest_framework import serializers
from apps.inventory.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
                'pk', 'name', 'price', 'description',
            )