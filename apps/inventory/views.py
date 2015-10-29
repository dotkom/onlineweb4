# API v1
import django_filters
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from apps.inventory.serializers import ItemSerializer
from apps.inventory.models import Item


class InventoryViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    queryset = Item.objects.filter(avalible=True)
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)


