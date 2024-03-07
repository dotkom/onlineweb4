import logging

from rest_framework import serializers

from apps.companyprofile.serializers import CompanySerializer
from apps.events.models import AttendanceEvent, CompanyEvent, Event, Extras, RuleBundle
from apps.gallery.serializers import ResponsiveImageSerializer

logger = logging.getLogger(__name__)


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = ("id", "choice", "note")


class RuleBundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleBundle
        fields = (
            "description",
            "field_of_study_rules",
            "grade_rules",
            "user_group_rules",
            "rule_strings",
            "id",
        )


class AttendanceEventSerializer(serializers.ModelSerializer):
    rule_bundles = RuleBundleSerializer(many=True)
    extras = ExtrasSerializer(many=True)

    class Meta:
        model = AttendanceEvent
        fields = (
            "id",
            "max_capacity",
            "waitlist",
            "guest_attendance",
            "registration_start",
            "registration_end",
            "unattend_deadline",
            "automatically_set_marks",
            "rule_bundles",
            "number_on_waitlist",
            "number_of_seats_taken",
            "extras",
        )


class CompanyEventSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = CompanyEvent
        fields = ("company", "event")


class EventSerializer(serializers.ModelSerializer):
    absolute_url = serializers.CharField(source="get_absolute_url", read_only=True)
    attendance_event = AttendanceEventSerializer()
    company_event = CompanyEventSerializer(many=True, source="company_events")
    image = ResponsiveImageSerializer()

    class Meta:
        model = Event
        fields = (
            "absolute_url",
            "attendance_event",
            "company_event",
            "description",
            "event_start",
            "event_end",
            "event_type",
            "id",
            "image",
            "ingress",
            "ingress_short",
            "location",
            "slug",
            "title",
            "organizer_name",
            "organizer",
        )
