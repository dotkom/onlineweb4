from django_filters import filters, filterset
from watson import search as watson_search

from .models import CareerOpportunity


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class WatsonFilter(filters.CharFilter):
    def filter(self, queryset, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset


class CareerOpportunityFilter(filterset.FilterSet):
    query = WatsonFilter()
    location = filters.CharFilter(field_name="location__slug")
    location__in = CharInFilter(field_name="location__slug", lookup_expr="in")

    class Meta:
        model = CareerOpportunity
        fields = {
            "start": ["gte", "lte"],
            "end": ["gte", "lte"],
            "deadline": ["gte", "lte"],
            "featured": ["exact"],
            "company": ["exact", "in"],
            "employment": ["exact", "in"],
        }
