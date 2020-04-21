import django_filters
from django_filters.filters import BaseInFilter, NumberFilter
from guardian.shortcuts import get_objects_for_user
from watson import search as watson_search

from apps.events.models import (
    AttendanceEvent,
    Attendee,
    Event,
    FieldOfStudyRule,
    GradeRule,
    RuleBundle,
    UserGroupRule,
)


class BaseNumberInFilter(BaseInFilter, NumberFilter):
    pass


class WatsonFilter(django_filters.CharFilter):
    def filter(self, queryset, value):
        if value and value != "":
            queryset = watson_search.filter(queryset, value)
        return queryset


class EventFilter(django_filters.FilterSet):
    event_start__gte = django_filters.DateTimeFilter(
        field_name="event_start", lookup_expr="gte"
    )
    event_start__lte = django_filters.DateTimeFilter(
        field_name="event_start", lookup_expr="lte"
    )
    event_end__gte = django_filters.DateTimeFilter(
        field_name="event_end", lookup_expr="gte"
    )
    event_end__lte = django_filters.DateTimeFilter(
        field_name="event_end", lookup_expr="lte"
    )
    attendance_event__isnull = django_filters.BooleanFilter(
        field_name="attendance_event", lookup_expr="isnull"
    )
    is_attendee = django_filters.BooleanFilter(
        field_name="attendance_event", method="filter_is_attendee"
    )
    can_change = django_filters.BooleanFilter(method="filter_can_change")
    can_attend = django_filters.BooleanFilter(method="filter_can_attend")
    event_type = BaseNumberInFilter(field_name="event_type", lookup_expr="in")
    companies = BaseNumberInFilter(field_name="companies", lookup_expr="in")
    query = WatsonFilter()

    def filter_can_attend(self, queryset, name, value):
        """
        Filter events based on if the user can attend said event.
        """

        """ User cannot attend events if they are not logged in """
        if not self.request.user.is_authenticated:
            return queryset.none()

        if value:
            events_with_attendance = queryset.filter(attendance_event__isnull=False)
            events_without_attendance = queryset.filter(attendance_event__isnull=True)
            user_attendable_event_pks = []
            for event in events_with_attendance:
                response = event.attendance_event.rules_satisfied(self.request.user)
                can_attend = response.get("status", None)
                if can_attend:
                    user_attendable_event_pks.append(event.id)

            user_attendable_events = events_with_attendance.filter(
                attendance_event__pk__in=user_attendable_event_pks
            )
            all_available_events = user_attendable_events | events_without_attendance
            return all_available_events

        return queryset.all()

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

    def filter_can_change(self, queryset, name, value):
        """
        Filter events based on if the user has permission to change them
        """

        """ If filter is set to False, don't filter """
        if not value:
            return queryset

        user = self.request.user
        """ User cannot attend events if they are not logged in """
        if not user.is_authenticated:
            return queryset.none()
        """ Don't filter on this field if user is a superuser """
        if user.is_superuser:
            return queryset

        allowed_events = get_objects_for_user(
            user, "events.change_event", accept_global_perms=False, klass=queryset
        )
        return allowed_events

    class Meta:
        model = Event
        fields = ("event_start", "event_end", "event_type", "is_attendee")


class ExtrasFilter(django_filters.FilterSet):
    event = django_filters.ModelChoiceFilter(
        field_name="attendanceevent", queryset=AttendanceEvent.objects.all()
    )
    query = WatsonFilter()


class RuleBundleFilter(django_filters.FilterSet):
    event = django_filters.ModelChoiceFilter(
        field_name="attendanceevent", queryset=AttendanceEvent.objects.all()
    )

    class Meta:
        model = RuleBundle
        fields = ("field_of_study_rules", "grade_rules", "user_group_rules")


class FieldOfStudyRuleFilter(django_filters.FilterSet):
    event = django_filters.ModelChoiceFilter(
        field_name="rulebundle__attendanceevent", queryset=AttendanceEvent.objects.all()
    )

    class Meta:
        model = FieldOfStudyRule
        fields = ("offset", "field_of_study")


class GradeRuleFilter(django_filters.FilterSet):
    event = django_filters.ModelChoiceFilter(
        field_name="rulebundle__attendanceevent", queryset=AttendanceEvent.objects.all()
    )

    class Meta:
        model = GradeRule
        fields = ("offset", "grade")


class UserGroupRuleFilter(django_filters.FilterSet):
    event = django_filters.ModelChoiceFilter(
        field_name="rulebundle__attendanceevent", queryset=AttendanceEvent.objects.all()
    )

    class Meta:
        model = UserGroupRule
        fields = ("offset", "group")
