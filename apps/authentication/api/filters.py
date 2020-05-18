import django_filters
from watson import search as watson_search

from ..models import OnlineUser


class UserFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method="watson_filter")

    def watson_filter(self, queryset, name, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset

    class Meta:
        model = OnlineUser
        fields = ("first_name", "last_name", "rfid", "query")
