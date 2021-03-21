import django_filters
from watson import search as watson_search

from ..models import GroupMember, OnlineGroup, OnlineUser


class UserFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method="watson_filter")

    def watson_filter(self, queryset, name, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset

    class Meta:
        model = OnlineUser
        fields = ("first_name", "last_name", "rfid", "query")


class OnlineGroupFilter(django_filters.FilterSet):
    members__user = django_filters.NumberFilter(field_name="members", lookup_expr="user_id")
    
    class Meta:
        model = OnlineGroup
        fields = ("name_short", "name_long", "parent_group", "group_type")
