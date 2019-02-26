import graphene

from apps.authentication.graphql_schema import Query as authentication_query
from apps.inventory.graphql_schema import Query as inventory_query
from apps.shop.graphql_schema import Query as shop_query


class Query(authentication_query, inventory_query, shop_query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
