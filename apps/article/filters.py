import django_filters
from watson import search as watson_search


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class ArticlesFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name='published_date', lookup_expr='year')
    month = django_filters.NumberFilter(field_name='published_date', lookup_expr='month')
    tags = django_filters.CharFilter(field_name='tags__name')
    tags_in = CharInFilter(field_name='tags__name', lookup_expr='in')
    query = django_filters.CharFilter(method='watson_filter')

    def watson_filter(self, queryset, name, value):
        if value and value != '':
            queryset = watson_search.filter(queryset, value)
        return queryset
