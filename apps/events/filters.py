import django_filters
from django_filters.filters import Lookup

from apps.events.models import Event


class ListFilter(django_filters.Filter):
    # https://github.com/carltongibson/django-filter/issues/137#issuecomment-37820702
    def filter(self, qs, value):
        value_list = value.split(u',')
        return super(ListFilter, self).filter(qs, Lookup(value_list, 'in'))


class EventDateFilter(django_filters.FilterSet):
    event_start__gte = django_filters.DateTimeFilter(name='event_start', lookup_expr='gte')
    event_start__lte = django_filters.DateTimeFilter(name='event_start', lookup_expr='lte')
    event_end__gte = django_filters.DateTimeFilter(name='event_end', lookup_expr='gte')
    event_end__lte = django_filters.DateTimeFilter(name='event_end', lookup_expr='lte')
    attendance_event__isnull = django_filters.BooleanFilter(name='attendance_event', lookup_expr='isnull')
    event_type = ListFilter()

    class Meta:
        model = Event
        fields = ('event_start', 'event_end', 'event_type')
