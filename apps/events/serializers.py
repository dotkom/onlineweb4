import logging

from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from onlineweb4.fields.recaptcha import RecaptchaField
from rest_framework import serializers, status
from rest_framework.serializers import ValidationError

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import UserReadOnlySerializer
from apps.companyprofile.serializers import CompanySerializer
from apps.events.constants import AttendStatus
from apps.events.models import (
    AttendanceEvent,
    Attendee,
    CompanyEvent,
    Event,
    Extras,
    RuleBundle,
)
from apps.gallery.serializers import ResponsiveImageSerializer
from apps.payment.serializers import PaymentReadOnlySerializer

logger = logging.getLogger(__name__)


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
            'organizer_name', 'organizer',
        )


class AttendSerializer(serializers.Serializer):
    rfid = serializers.CharField()
    event = serializers.IntegerField(required=True)


class RegisterAttendanceError(serializers.ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'
    default_code = 'invalid'

    def __init__(self, attend_status: int, detail=None):
        self.detail = {
            'detail': {
                'message': detail,
                'attend_status': attend_status,
            },
        }


class RegisterAttendanceSerializer(serializers.Serializer):
    rfid = serializers.CharField(required=False, allow_null=True)
    username = serializers.CharField(required=False, allow_null=True)
    event = serializers.IntegerField(required=False)
    approved = serializers.BooleanField(required=False)

    def _validate_rfid(self, rfid: str):
        return rfid

    def _validate_username(self, username: str):
        if username:
            username_exists = User.objects.filter(username=username).exists()
            if not username_exists:
                raise RegisterAttendanceError(
                    detail='Brukernavnet finnes ikke. Husk at det er et online.ntnu.no brukernavn! '
                           '(Prøv igjen, eller scan nytt kort for å avbryte.)',
                    attend_status=AttendStatus.USERNAME_DOES_NOT_EXIST,
                )

        return username

    def _validate_event(self, event_id: int):
        if not event_id:
            raise RegisterAttendanceError(
                detail='Arrangementets id er ikke oppgitt',
                attend_status=AttendStatus.EVENT_ID_MISSING,
            )

        try:
            event = Event.objects.get(pk=event_id)
            admin_user = self.context.get('request').user
            if not admin_user.has_perm('events.change_event', event):
                raise RegisterAttendanceError(
                    detail='Administerende bruker har ikke rettigheter til å registrere oppmøte på dette arrangementet',
                    attend_status=AttendStatus.NOT_AUTHORIZED,
                )
        except Event.DoesNotExist:
            raise RegisterAttendanceError(
                detail='Det gitte arrangementet eksisterer ikke',
                attend_status=AttendStatus.EVENT_DOES_NOT_EXIST,
            )

        return event_id

    def _handle_attendee(self, attendee: Attendee, waitlist_approved: bool):
        # If attendee is already marked as attended
        if attendee.attended:
            logger.debug(f'Attendee ({attendee}) already marked as attended.')
            raise RegisterAttendanceError(
                detail=f'{attendee.user} har allerede registrert oppmøte.',
                attend_status=AttendStatus.PREVIOUSLY_REGISTERED,
            )

        # If attendee is on waitlist (bypassed if attendee has gotten the all-clear)
        if attendee.is_on_waitlist() and not waitlist_approved:
            raise RegisterAttendanceError(
                detail=f'{attendee.user} er på venteliste. Registrer dem som møtt opp allikevel?',
                attend_status=AttendStatus.ON_WAIT_LIST,
            )

    def get_attendee(self, data: dict):
        username: str = data.get('username')
        rfid: str = data.get('rfid')
        event_id: int = data.get('event')
        user = User.objects.get(Q(username=username) | Q(rfid=rfid, rfid__isnull=False))
        return Attendee.objects.get(user=user, event_id=event_id)

    def validate(self, attrs: dict):
        admin_user: User = self.context.get('request').user
        username: str = attrs.get('username')
        rfid: str = attrs.get('rfid')
        event_id: int = attrs.get('event')
        waitlist_approved: bool = attrs.get('approved')

        self._validate_rfid(rfid)
        self._validate_username(username)
        self._validate_event(event_id)

        if not admin_user.is_authenticated:
            raise RegisterAttendanceError(
                detail='Administerende bruker må være logget inn for å registrere oppmøte',
                attend_status=AttendStatus.NOT_LOGGED_IN,
            )

        if not (username or rfid):
            raise RegisterAttendanceError(
                detail='Mangler både RFID og brukernavn. Vennligst prøv igjen.',
                attend_status=AttendStatus.USERNAME_AND_RFID_MISSING,
            )

        if username and rfid:
            try:
                user = User.objects.get(username=username)
                user.rfid = rfid
                user.save()
                logger.debug(f'Storing new RFID to user "{user}"', extra={'user': user.pk, 'rfid': rfid})
            except (IntegrityError, ValidationError):
                logger.error(f'Could not store RFID information for username "{username}" with RFID "{rfid}".')
                raise RegisterAttendanceError(
                    detail='Det oppstod en feil da vi prøvde å lagre informasjonen. Vennligst prøv igjen. '
                           'Dersom problemet vedvarer, ta kontakt med dotkom. '
                           'Personen kan registreres med brukernavn i steden for RFID.',
                    attend_status=AttendStatus.REGISTER_ERROR,
                )

        try:
            attendee = self.get_attendee(attrs)
            self._handle_attendee(attendee, waitlist_approved)
        except Attendee.DoesNotExist:
            raise RegisterAttendanceError(
                detail='Brukeren er ikke påmeldt dette arrangementet',
                attend_status=AttendStatus.USER_NOT_ATTENDING,
            )
        except User.DoesNotExist:
            # If attendee tried to attend by a username that isn't tied to a user
            if not rfid:
                raise RegisterAttendanceError(
                    detail='Brukernavnet finnes ikke. Husk at det er et online.ntnu.no brukernavn! '
                           '(Prøv igjen, eller scan nytt kort for å avbryte.)',
                    attend_status=AttendStatus.USERNAME_DOES_NOT_EXIST,
                )

            # If attendee tried to attend by card, but card isn't tied to a user
            else:
                raise RegisterAttendanceError(
                    detail='Kortet finnes ikke i databasen. Skriv inn et online.ntnu.no brukernavn for å '
                           'knytte kortet til brukeren og registrere oppmøte.',
                    attend_status=AttendStatus.RFID_DOES_NOT_EXIST,
                )

        return attrs
