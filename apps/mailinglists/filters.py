import logging

from django_filters import filters, filterset
from watson import search as watson_search

logger = logging.getLogger(__name__)


class WatsonFilter(filters.CharFilter):
    def filter(self, queryset, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset


class MailGroupFilter(filterset.FilterSet):
    public = filters.BooleanFilter(field_name="public")
    query = WatsonFilter()
