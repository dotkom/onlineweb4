import django_filters
from django_filters.filters import BaseInFilter, NumberFilter

from apps.events.models import Attendee, Event

class EventTypeInFilter(BaseInFilter, NumberFilter):
    pass

class EventDateFilter(django_filters.FilterSet):
    event_start__gte = django_filters.DateTimeFilter(field_name='event_start', lookup_expr='gte')
    event_start__lte = django_filters.DateTimeFilter(field_name='event_start', lookup_expr='lte')
    event_end__gte = django_filters.DateTimeFilter(field_name='event_end', lookup_expr='gte')
    event_end__lte = django_filters.DateTimeFilter(field_name='event_end', lookup_expr='lte')
    attendance_event__isnull = django_filters.BooleanFilter(field_name='attendance_event', lookup_expr='isnull')
    is_attendee = django_filters.BooleanFilter(field_name='attendance_event', method='filter_is_attendee')
    event_type = EventTypeInFilter(field_name='event_type', lookup_expr='in')

    def filter_is_attendee(self, queryset, name, value):
        """
        Filter events based on if a user is attending them or not.
        """

        """ User cannot attend events if they are not logged in """
        if not self.request.user.is_authenticated:
            return queryset.none()

        user_attendees = Attendee.objects.filter(user=self.request.user)
        attending_events = [attendee.event.pk for attendee in user_attendees]
        if value:
            return queryset.filter(pk__in=attending_events)
        return queryset.all()

    class Meta:
        model = Event
        fields = ('event_start', 'event_end', 'event_type', 'is_attendee')
