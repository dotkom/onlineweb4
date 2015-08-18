from rest_framework import serializers
from apps.events.models import AttendanceEvent, Attendee, CompanyEvent, Event, RuleBundle
from apps.authentication.serializers import UserSerializer


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = (
                '',
            )


class EventSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Event
        fields = (
                'absolute_url', 'attendance_event', 'author', 'description', 'event_start', 'event_end',
                'event_type', 'id', 'images', 'ingress', 'ingress_short', 'location', 'slug', 'title',
            )


class RuleBundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleBundle
        fields = (
                'description', 'field_of_study_rules', 'grade_rules', 'user_group_rules',
            )


class AttendanceEventSerializer(serializers.ModelSerializer):
    event = EventSerializer()
    rule_bundles = RuleBundleSerializer(many=True)

    class Meta:
        model = AttendanceEvent
        fields = (
                'event',
                'max_capacity', 'waitlist', 'guest_attendance',
                'registration_start', 'registration_end', 'unattend_deadline',
                'automatically_set_marks', 'rule_bundles',
            )


class CompanyEventSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = CompanyEvent
        fields = (
                'absolute_url', 'attendance_event', 'author', 'company_event', 'description', 'event_start', 'event_end',
                'event_type', 'id', 'images', 'ingress', 'ingress_short', 'location', 'slug', 'title',
            )
