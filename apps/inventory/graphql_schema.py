from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from .models import Batch, Item, ItemCategory


class BatchNode(DjangoObjectType):

    class Meta:
        model = Batch
        interfaces = (relay.Node,)


class ItemNode(DjangoObjectType):

    class Meta:
        model = Item
        interfaces = (relay.Node,)


class ItemCategoryNode(DjangoObjectType):

    class Meta:
        model = ItemCategory
        interfaces = (relay.Node,)


# Top level Query schema for apps.inventory
class Query(object):
    item = relay.Node.Field(ItemNode)
    all_items = DjangoConnectionField(ItemNode)

    item_category = relay.Node.Field(ItemCategoryNode)
    all_item_categories = DjangoConnectionField(ItemCategoryNode)
