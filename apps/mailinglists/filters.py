import logging

from django_filters import filters, filterset
from watson import search as watson_search

from .models import MailGroup, MailEntity

logger = logging.getLogger(__name__)


class WatsonFilter(filters.CharFilter):
    def filter(self, queryset, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset


class MailGroupFilter(filterset.FilterSet):
    query = WatsonFilter()

    class Meta:
        model = MailGroup
        fields = ("domain", "public")


class MailEntityFilter(filterset.FilterSet):
    query = WatsonFilter()

    class Meta:
        model = MailEntity
        fields = ("groups", "public")
