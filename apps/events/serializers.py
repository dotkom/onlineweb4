from django.utils import timezone
from onlineweb4.fields.recaptcha import RecaptchaField
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import UserReadOnlySerializer
from apps.companyprofile.serializers import CompanySerializer
from apps.events.models import AttendanceEvent, Attendee, CompanyEvent, Event, Extras, RuleBundle
from apps.gallery.serializers import ResponsiveImageSerializer
from apps.payment.serializers import PaymentReadOnlySerializer


class ExtrasSerializer(serializers.ModelSerializer):

    class Meta:
        model = Extras
        fields = ('id', 'choice', 'note',)


class AttendeeRegistrationReadOnlySerializer(serializers.ModelSerializer):
    user = UserReadOnlySerializer(read_only=True)
    extras = ExtrasSerializer(read_only=True)
    event = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    class Meta:
        model = Attendee
        fields = (
            'id', 'event', 'user', 'attended', 'timestamp', 'show_as_attending_event', 'has_paid', 'extras',
        )
        read_only = True


class AttendeeRegistrationCreateSerializer(serializers.ModelSerializer):
    extras = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        write_only=True,
        queryset=Extras.objects.all(),
    )
    user = serializers.PrimaryKeyRelatedField(
        write_only=True,
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
    )
    event = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=AttendanceEvent.objects.all(),
    )
    recaptcha = RecaptchaField()

    def validate_user(self, user):
        request = self.context.get('request')
        if not request:
            raise ValidationError('internal:Request was not passed as context to serializer')

        if user.id != request.user.id:
            raise ValidationError('Du kan ikke melde andre brukere på arrangementer!')

        return user

    def validate(self, data):
        request = self.context.get('request', None)
        if not request:
            raise ValidationError('internal:Request was not passed as context to serializer')

        user = request.user
        if not user.is_authenticated:
            raise ValidationError('Du må være logget inn for å kunne melde deg på et arrangement')

        attendance_event = data.get('event', None)
        event = attendance_event.event

        if not event:
            raise ValidationError('Det gitte arrangementet eksisterer ikke')

        if not event.is_attendance_event():
            raise ValidationError('Dette er ikke et påmeldingsarrangement')

        attend_response = attendance_event.is_eligible_for_signup(request.user)
        can_attend = attend_response.get('status')

        if not can_attend:
            raise ValidationError(attend_response.get('message'))

        return data

    def create(self, validated_data):
        """
        The recaptcha field is not part of the model, but will still need to be validated.
        All serializer fields will be put into 'Model#create', and 'recaptcha' is removed for the serializer not
        to try and create it on the model-
        """
        validated_data.pop('recaptcha')
        return super(AttendeeRegistrationCreateSerializer, self).create(validated_data)

    class Meta:
        model = Attendee
        fields = (
            'id', 'event', 'user', 'show_as_attending_event', 'recaptcha', 'extras',
        )


class AttendeeRegistrationUpdateSerializer(serializers.ModelSerializer):
    extras = serializers.PrimaryKeyRelatedField(
        required=False,
        allow_null=True,
        write_only=True,
        queryset=Extras.objects.all()
    )

    def validate_extras(self, value):
        attendance = self.instance.event
        if timezone.now() > attendance.registration_end:
            raise ValidationError('Det er ikke mulig å endre ekstravalg etter påmeldingsfristen')
        if timezone.now() > attendance.unattend_deadline:
            raise ValidationError('Det er ikke mulig å endre ekstravalg etter avmeldingsfristen')

        return value

    class Meta:
        model = Attendee
        fields = (
            'id', 'user', 'show_as_attending_event', 'extras',
        )


class AttendeeSerializer(serializers.ModelSerializer):
    user = UserReadOnlySerializer()

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
    extras = ExtrasSerializer(many=True)
    payments = serializers.SerializerMethodField()

    has_postponed_registration = SerializerUserMethodField()
    is_marked = SerializerUserMethodField()
    is_suspended = SerializerUserMethodField()
    is_eligible_for_signup = SerializerUserMethodField()
    is_attendee = SerializerUserMethodField()
    is_on_waitlist = SerializerUserMethodField()
    what_place_is_user_on_wait_list = SerializerUserMethodField()

    def get_payments(self, obj):
        payments = obj.get_payments()
        serialized_payments = PaymentReadOnlySerializer(payments, many=True)
        return serialized_payments.data

    class Meta:
        model = AttendanceEvent
        fields = (
            'max_capacity', 'waitlist', 'guest_attendance', 'extras', 'payments',
            'registration_start', 'registration_end', 'unattend_deadline',
            'automatically_set_marks', 'rule_bundles', 'number_on_waitlist',
            'number_of_seats_taken', 'visible_attending_attendees', 'has_extras',
            'has_reservation', 'has_postponed_registration', 'is_marked', 'is_suspended',
            'is_eligible_for_signup', 'is_attendee', 'is_on_waitlist', 'what_place_is_user_on_wait_list'
        )


class AttendanceEventSerializer(serializers.ModelSerializer):
    rule_bundles = RuleBundleSerializer(many=True)
    extras = ExtrasSerializer(many=True)

    class Meta:
        model = AttendanceEvent
        fields = (
            'max_capacity', 'waitlist', 'guest_attendance',
            'registration_start', 'registration_end', 'unattend_deadline',
            'automatically_set_marks', 'rule_bundles', 'number_on_waitlist',
            'number_of_seats_taken', 'extras',
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
