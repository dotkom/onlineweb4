from rest_framework import serializers
from rest_framework_recaptcha.fields import ReCaptchaField

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import UserSerializer
from apps.companyprofile.serializers import CompanySerializer
from apps.events.models import AttendanceEvent, Attendee, CompanyEvent, Event, RuleBundle
from apps.gallery.serializers import ResponsiveImageSerializer


class UserAttendeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='user',
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    event = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='event',
        queryset=AttendanceEvent.objects.all()
    )
    recaptcha = ReCaptchaField()

    class Meta:
        model = Attendee
        fields = (
            'id', 'event', 'user', 'attended', 'timestamp', 'event_id', 'user_id', 'show_as_attending_event',
            'has_paid', 'recaptcha',
        )
        read_only_fields = ('event', 'user', 'id', 'timestamp', 'has_paid')


class AttendeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Attendee
        fields = (
            'id', 'event', 'user', 'attended', 'timestamp',
        )


class RuleBundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleBundle
        fields = (
            'description', 'field_of_study_rules', 'grade_rules', 'user_group_rules',
            'rule_strings', 'id',
        )


class SerializerUserMethodField(serializers.SerializerMethodField):
    """
    Serialize a field related to a user.
    Gets a field from a model instance with only the user as an arguemnt.
    """

    def bind(self, field_name, parent):
        if self.method_name is None:
            self.method_name = field_name
        super(SerializerUserMethodField, self).bind(field_name, parent)

    def to_representation(self, obj):
        request = self.context.get('request', None)
        if request:
            get_user_field_method = getattr(obj, self.method_name)
            return get_user_field_method(request.user)
        return None


class UserAttendanceEventSerializer(serializers.ModelSerializer):
    rule_bundles = RuleBundleSerializer(many=True)
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
            'max_capacity', 'waitlist', 'guest_attendance',
            'registration_start', 'registration_end', 'unattend_deadline',
            'automatically_set_marks', 'rule_bundles', 'number_on_waitlist',
            'number_of_seats_taken', 'visible_attending_attendees', 'has_extras',
            'has_reservation', 'has_postponed_registration', 'is_marked', 'is_suspended',
            'is_eligible_for_signup', 'is_attendee', 'is_on_waitlist', 'what_place_is_user_on_wait_list'
        )


class AttendanceEventSerializer(serializers.ModelSerializer):
    rule_bundles = RuleBundleSerializer(many=True)

    class Meta:
        model = AttendanceEvent
        fields = (
            'max_capacity', 'waitlist', 'guest_attendance',
            'registration_start', 'registration_end', 'unattend_deadline',
            'automatically_set_marks', 'rule_bundles', 'number_on_waitlist',
            'number_of_seats_taken',
        )


class CompanyEventSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = CompanyEvent
        fields = (
            'company', 'event',
        )


class EventSerializer(serializers.ModelSerializer):
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)
    attendance_event = AttendanceEventSerializer()
    company_event = CompanyEventSerializer(many=True)
    image = ResponsiveImageSerializer()

    class Meta:
        model = Event
        fields = (
            'absolute_url', 'attendance_event', 'company_event', 'description', 'event_start', 'event_end',
            'event_type', 'id', 'image', 'ingress', 'ingress_short', 'location', 'slug', 'title',
            'organizer_name',
        )


class AttendSerializer(serializers.Serializer):
    rfid = serializers.CharField()
    event = serializers.IntegerField(required=True)
