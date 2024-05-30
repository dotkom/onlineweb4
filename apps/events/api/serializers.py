from random import choice as random_choice

from django.utils import timezone
from rest_framework import fields, serializers

from apps.authentication.serializers import UserReadOnlySerializer
from apps.events.models import AttendanceEvent
from apps.gallery.serializers import ResponsiveImageSerializer
from onlineweb4.fields.turnstile import TurnstileField

from ..models import (
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


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = ("id", "choice", "note")


class AttendanceResultSerializer(serializers.Serializer):
    status = fields.BooleanField()
    message = fields.CharField()
    status_code = fields.IntegerField()
    offset = fields.DateTimeField(allow_null=True)


class AttendeeInfoSerializer(serializers.Serializer):
    is_attendee = fields.BooleanField()
    is_on_waitlist = fields.BooleanField()
    is_eligible_for_signup = AttendanceResultSerializer()


class EventSerializer(serializers.ModelSerializer):
    images = ResponsiveImageSerializer(many=True)
    author = UserReadOnlySerializer()
    event_type_display = serializers.CharField(
        source="get_event_type_display", read_only=True
    )
    start_date = serializers.DateTimeField(source="event_start")
    end_date = serializers.DateTimeField(source="event_end")
    is_attendance_event = serializers.BooleanField(read_only=True)
    max_capacity = serializers.IntegerField(source="attendance_event.max_capacity")
    waitlist = serializers.BooleanField(source="attendance_event.waitlist")
    number_of_seats_taken = serializers.IntegerField(
        source="attendance_event.number_of_seats_taken"
    )
    companies = serializers.StringRelatedField(many=True)
    attendee_info = serializers.SerializerMethodField()

    def get_attendee_info(self, instance: Event):
        user = self.context["request"].user
        if (
            user.is_authenticated
            and hasattr(instance, "attendance_event")
            and (attendance_event := instance.attendance_event)
        ):
            return {
                "is_attendee": attendance_event.is_attendee(user),
                "is_on_waitlist": attendance_event.is_on_waitlist(user),
                "is_eligible_for_signup": AttendanceResultSerializer(
                    attendance_event.is_eligible_for_signup(user)
                ).data,
            }

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
            "max_capacity",
            "waitlist",
            "number_of_seats_taken",
            "attendee_info",
        )


class AttendanceEventSerializer(serializers.ModelSerializer):
    extras = ExtrasSerializer(many=True)
    feedback = serializers.PrimaryKeyRelatedField(read_only=True, source="get_feedback")
    payment = serializers.PrimaryKeyRelatedField(read_only=True)
    is_marked = SerializerUserMethodField()
    is_suspended = SerializerUserMethodField()
    is_eligible_for_signup = fields.SerializerMethodField()
    is_attendee = SerializerUserMethodField()
    is_on_waitlist = SerializerUserMethodField()
    what_place_is_user_on_wait_list = SerializerUserMethodField()

    def get_is_eligible_for_signup(self, attendance_event: AttendanceEvent):
        user = self.context["request"].user
        if user.is_authenticated:
            return AttendanceResultSerializer(
                attendance_event.is_eligible_for_signup(user)
            ).data

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

    turnstile = TurnstileField()
    allow_pictures = serializers.BooleanField(required=False)
    show_as_attending_event = serializers.BooleanField(required=False)
    note = serializers.CharField(default="", max_length=100)


class AttendeeSerializer(serializers.ModelSerializer):
    user = UserReadOnlySerializer(read_only=True)
    extras = serializers.PrimaryKeyRelatedField(
        required=False, allow_null=True, queryset=Extras.objects.all()
    )

    def validate_extras(self, extra):
        if self.instance:
            attendance: AttendanceEvent = self.instance.event
            allowedExtras = Extras.objects.filter(attendanceevent=attendance)
            now = timezone.now()

            if now > attendance.unattend_deadline and attendance.registration_end < now:
                raise serializers.ValidationError("Du kan ikke lenger endre påmelding")

            if extra and extra not in allowedExtras:
                raise serializers.ValidationError(
                    "Det er ikke mulig å velge ekstravalg som ikke er på event"
                )

        return extra

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
        fields = (
            "id",
            "event",
            "full_name",
            "is_visible",
            "year_of_study",
            "field_of_study",
        )


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
