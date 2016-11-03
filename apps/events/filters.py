import django_filters

from apps.events.models import Event


class EventDateFilter(django_filters.FilterSet):
    event_start__gte = django_filters.DateTimeFilter(name='event_start', lookup_type='gte')
    event_start__lte = django_filters.DateTimeFilter(name='event_start', lookup_type='lte')
    event_end__gte = django_filters.DateTimeFilter(name='event_end', lookup_type='gte')
    event_end__lte = django_filters.DateTimeFilter(name='event_end', lookup_type='lte')

    class Meta:
        model = Event
        fields = ('event_start', 'event_end', 'event_type')
