from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from ..inventory.graphql_schema import ItemNode
from ..inventory.models import Item
from .models import Order, OrderLine


class OrderNode(DjangoObjectType):
    content_object = DjangoConnectionField(ItemNode)

    class Meta:
        model = Order
        interfaces = (relay.Node,)

    def resolve_content_object(self, info):
        # Not really sure what to do in this case.
        # We expect the object to be an ItemNode, but what should we do if it isn't?
        # Return None? Error out? (Errors marks the field as null and sends the raised exception)
        if self.content_object.__class__.__name__ != Item.__name__:
            raise ValueError("Content object on Order has invalid type for this query {} vs {}."
                             .format(self.content_object.__class__.__name__, Item.__name__))


class OrderLineNode(DjangoObjectType):

    class Meta:
        model = OrderLine
        interfaces = (relay.Node,)


# Top level Query schema for apps.shop
class Query(object):
    order = relay.Node.Field(OrderNode)
    all_orders = DjangoConnectionField(OrderNode)

    orderline = relay.Node.Field(OrderLineNode)
    all_orderlines = DjangoConnectionField(OrderLineNode)
