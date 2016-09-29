from rest_framework import serializers

from apps.authentication.serializers import UserSerializer
from apps.companyprofile.serializers import CompanySerializer
from apps.events.models import AttendanceEvent, Attendee, CompanyEvent, Event, RuleBundle


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = (
            'event', 'user', 'attended', 'timestamp',
        )


class RuleBundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleBundle
        fields = (
            'description', 'field_of_study_rules', 'grade_rules', 'user_group_rules',
        )


class AttendanceEventSerializer(serializers.ModelSerializer):
    rule_bundles = RuleBundleSerializer(many=True)

    class Meta:
        model = AttendanceEvent
        fields = (
            'max_capacity', 'waitlist', 'guest_attendance',
            'registration_start', 'registration_end', 'unattend_deadline',
            'automatically_set_marks', 'rule_bundles',
        )


class CompanyEventSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = CompanyEvent
        fields = (
            'company', 'event',
        )


class EventSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)
    attendance_event = AttendanceEventSerializer()
    company_event = CompanyEventSerializer(many=True)

    class Meta:
        model = Event
        fields = (
            'absolute_url', 'attendance_event', 'company_event', 'author', 'description', 'event_start', 'event_end',
            'event_type', 'id', 'images', 'ingress', 'ingress_short', 'location', 'slug', 'title',
        )


class AttendSerializer(serializers.Serializer):
    rfid = serializers.CharField()
    event = serializers.PrimaryKeyRelatedField(read_only=True)
