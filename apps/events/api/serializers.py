from random import choice as random_choice

from django.utils import timezone
from onlineweb4.fields.recaptcha import RecaptchaField
from rest_framework import serializers

from apps.authentication.serializers import UserReadOnlySerializer
from apps.gallery.serializers import ResponsiveImageSerializer

from ..models import (
    AttendanceEvent,
    Attendee,
    Event,
    Extras,
    FieldOfStudyRule,
    GradeRule,
    RuleBundle,
    UserGroupRule,
)
from .constants import ANONYMOUS_ATTENDEE_NAMES
from .fields import SerializerUserMethodField


class EventSerializer(serializers.ModelSerializer):
    images = ResponsiveImageSerializer(many=True)
    author = UserReadOnlySerializer()
    event_type_display = serializers.CharField(
        source="get_event_type_display", read_only=True
    )
    start_date = serializers.DateTimeField(source="event_start")
    end_date = serializers.DateTimeField(source="event_end")
    is_attendance_event = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "slug",
            "ingress",
            "ingress_short",
            "description",
            "start_date",
            "end_date",
            "location",
            "event_type",
            "event_type_display",
            "organizer",
            "author",
            "images",
            "companies",
            "is_attendance_event",
        )


class AttendanceEventSerializer(serializers.ModelSerializer):
    feedback = serializers.PrimaryKeyRelatedField(read_only=True, source="get_feedback")
    payment = serializers.PrimaryKeyRelatedField(read_only=True)
    has_postponed_registration = SerializerUserMethodField()
    is_marked = SerializerUserMethodField()
    is_suspended = SerializerUserMethodField()
    is_eligible_for_signup = SerializerUserMethodField()
    is_attendee = SerializerUserMethodField()
    is_on_waitlist = SerializerUserMethodField()
    what_place_is_user_on_wait_list = SerializerUserMethodField()

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
            "has_feedback",
            "has_extras",
            "has_reservation",
            "extras",
            "payment",
            "feedback",
            "has_postponed_registration",
            "is_marked",
            "is_suspended",
            "is_eligible_for_signup",
            "is_attendee",
            "is_on_waitlist",
            "what_place_is_user_on_wait_list",
        )


class RegisterSerializer(serializers.Serializer):
    """
    Serializer used when a user attempts to register for an event
    """

    recaptcha = RecaptchaField()
    allow_pictures = serializers.BooleanField(default=False)
    show_as_attending_event = serializers.BooleanField(default=False)
    note = serializers.CharField(default="", max_length=100)


class AttendeeSerializer(serializers.ModelSerializer):
    user = UserReadOnlySerializer(read_only=True)
    extras = serializers.PrimaryKeyRelatedField(
        required=False, allow_null=True, write_only=True, queryset=Extras.objects.all()
    )

    def validate_extras(self, values):
        if self.instance:
            attendance: AttendanceEvent = self.instance.event
            if timezone.now() > attendance.registration_end:
                raise serializers.ValidationError(
                    "Det er ikke mulig å endre ekstravalg etter påmeldingsfristen"
                )
            if timezone.now() > attendance.unattend_deadline:
                raise serializers.ValidationError(
                    "Det er ikke mulig å endre ekstravalg etter avmeldingsfristen"
                )

            for extra in values:
                if extra not in attendance.extras:
                    raise serializers.ValidationError(
                        "Enkelte av ekstravalgene er ikke gyldige for dette arrangementet"
                    )

        return values

    class Meta:
        model = Attendee
        fields = (
            "id",
            "event",
            "user",
            "attended",
            "timestamp",
            "show_as_attending_event",
            "allow_pictures",
            "paid",
            "has_paid",
            "extras",
            "note",
        )


class AttendeeUpdateSerializer(AttendeeSerializer):
    """
    Users are allowed to change their attendees, but only a specific set of fields.
    """

    class Meta:
        model = Attendee
        fields = AttendeeSerializer.Meta.fields
        read_only_fields = (
            "event",
            "user",
            "attended",
            "timestamp",
            "paid",
            "has_paid",
        )


class AttendeeAdministrateSerializer(AttendeeSerializer):
    """
    Admins are allowed to change other users attendees, but only a specific set of fields.
    Admins should not be able to change things such as consents or notes.
    """

    class Meta:
        model = Attendee
        fields = AttendeeSerializer.Meta.fields
        read_only_fields = (
            "event",
            "user",
            "timestamp",
            "has_paid",
            "note",
            "extras",
            "show_as_attending_event",
            "allow_pictures",
        )


class PublicAttendeeSerializer(serializers.ModelSerializer):
    """
    Serialize users in the public attendee list.
    """

    full_name = serializers.SerializerMethodField()
    is_visible = serializers.BooleanField(source="show_as_attending_event")
    year_of_study = serializers.IntegerField(source="user.year")
    field_of_study = serializers.CharField(source="user.get_field_of_study_display")

    def get_full_name(self, attendee: Attendee):
        if attendee.show_as_attending_event:
            return attendee.user.get_full_name()
        return random_choice(ANONYMOUS_ATTENDEE_NAMES)

    class Meta:
        model = Attendee
        fields = ("id", "full_name", "is_visible", "year_of_study", "field_of_study")


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = ("id", "choice", "note")


class RuleBundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleBundle
        fields = (
            "id",
            "description",
            "field_of_study_rules",
            "grade_rules",
            "user_group_rules",
            "rule_strings",
        )


class FieldOfStudyRuleSerializer(serializers.ModelSerializer):
    field_of_study_display = serializers.CharField(source="get_field_of_study_display")

    class Meta:
        model = FieldOfStudyRule
        fields = ("id", "offset", "field_of_study", "field_of_study_display")


class GradeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeRule
        fields = ("id", "offset", "grade")


class UserGroupRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroupRule
        fields = ("id", "offset", "group")
