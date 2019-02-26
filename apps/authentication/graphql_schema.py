from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from .models import OnlineUser


class OnlineUserNode(DjangoObjectType):

    class Meta:
        model = OnlineUser
        interfaces = (relay.Node,)
        only_fields = ('first_name', 'last_name', 'rfid',)


# Top level Query schema for apps.authentication
class Query(object):
    user = relay.Node.Field(OnlineUserNode)
    all_users = DjangoConnectionField(OnlineUserNode)
