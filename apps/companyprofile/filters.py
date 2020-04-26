from django_filters import filters, filterset
from watson import search as watson_search

from .models import Company


class WatsonFilter(filters.CharFilter):
    def filter(self, queryset, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset


class CompanyFilter(filterset.FilterSet):
    query = WatsonFilter()

    class Meta:
        model = Company
        fields = {"name": ["exact"]}
