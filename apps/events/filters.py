import logging

import django_filters
from django_filters.filters import Lookup

from apps.events.models import AttendanceEvent, Attendee, Event


class ListFilter(django_filters.Filter):
    # https://github.com/carltongibson/django-filter/issues/137#issuecomment-37820702
    def filter(self, qs, value):
        value_list = value.split(u',')
        return super(ListFilter, self).filter(qs, Lookup(value_list, 'in'))


class EventDateFilter(django_filters.FilterSet):
    event_start__gte = django_filters.DateTimeFilter(field_name='event_start', lookup_expr='gte')
    event_start__lte = django_filters.DateTimeFilter(field_name='event_start', lookup_expr='lte')
    event_end__gte = django_filters.DateTimeFilter(field_name='event_end', lookup_expr='gte')
    event_end__lte = django_filters.DateTimeFilter(field_name='event_end', lookup_expr='lte')
    attendance_event__isnull = django_filters.BooleanFilter(field_name='attendance_event', lookup_expr='isnull')
    can_attend = django_filters.BooleanFilter(field_name='attendance_event', method='filter_can_attend')
    is_attending = django_filters.BooleanFilter(field_name='attendance_event', method='filter_is_attending')
    event_type = ListFilter()

    def filter_can_attend(self, queryset, name, value):
        """
        Filter events on if a user can attend an the related attendance_event.
        """

        """ Users cannot attend events if they are not logged in """
        if not self.request.user.is_authenticated:
            return queryset.none()

        attendance_events = AttendanceEvent.objects.all()
        possible_attendance_events = []
        for a_event in attendance_events:
            if a_event.user_can_attend(self.request.user):
                possible_attendance_events.append(a_event.pk)

        if value:
            return queryset.filter(pk__in=possible_attendance_events)
        else:
            return queryset.exclude(pk__in=possible_attendance_events)

    def filter_is_attending(self, queryset, name, value):
        """
        Filter events on if a user can attend them or not.
        """

        """ User cannot attend events if they are not logged in """
        if not self.request.user.is_authenticated:
            return queryset.none()

        user_attendees = Attendee.objects.filter(user=self.request.user)
        attending_events = [attendee.event.pk for attendee in user_attendees]
        if value:
            return queryset.filter(pk__in=attending_events)
        else:
            return queryset.exclude(pk__in=attending_events)

    class Meta:
        model = Event
        fields = ('event_start', 'event_end', 'event_type', 'can_attend', 'is_attending')
