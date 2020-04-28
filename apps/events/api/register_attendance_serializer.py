import logging

from django.db import IntegrityError
from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.serializers import ValidationError

from apps.authentication.models import OnlineUser as User
from apps.events.constants import AttendStatus
from apps.events.models import Attendee, Event

logger = logging.getLogger(__name__)


class RegisterAttendanceError(serializers.ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid input."
    default_code = "invalid"

    def __init__(self, attend_status: int, detail=None):
        self.detail = {"detail": {"message": detail, "attend_status": attend_status}}


class RegisterAttendanceSerializer(serializers.Serializer):
    rfid = serializers.CharField(required=False, allow_null=True, allow_blank=True)
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
                    detail="Brukernavnet finnes ikke. Husk at det er et online.ntnu.no brukernavn! "
                    "(Prøv igjen, eller scan nytt kort for å avbryte.)",
                    attend_status=AttendStatus.USERNAME_DOES_NOT_EXIST,
                )

        return username

    def _validate_event(self, event_id: int):
        if not event_id:
            raise RegisterAttendanceError(
                detail="Arrangementets id er ikke oppgitt",
                attend_status=AttendStatus.EVENT_ID_MISSING,
            )

        try:
            event = Event.objects.get(pk=event_id)
            admin_user = self.context.get("request").user
            if not admin_user.has_perm("events.change_event", event):
                raise RegisterAttendanceError(
                    detail="Administerende bruker har ikke rettigheter til å registrere oppmøte på dette arrangementet",
                    attend_status=AttendStatus.NOT_AUTHORIZED,
                )
        except Event.DoesNotExist:
            raise RegisterAttendanceError(
                detail="Det gitte arrangementet eksisterer ikke",
                attend_status=AttendStatus.EVENT_DOES_NOT_EXIST,
            )

        return event_id

    def _handle_attendee(self, attendee: Attendee, waitlist_approved: bool):
        # If attendee is already marked as attended
        if attendee.attended:
            logger.debug(f"Attendee ({attendee}) already marked as attended.")
            raise RegisterAttendanceError(
                detail=f"{attendee.user} har allerede registrert oppmøte.",
                attend_status=AttendStatus.PREVIOUSLY_REGISTERED,
            )

        # If attendee is on waitlist (bypassed if attendee has gotten the all-clear)
        if attendee.is_on_waitlist() and not waitlist_approved:
            raise RegisterAttendanceError(
                detail=f"{attendee.user} er på venteliste. Registrer dem som møtt opp allikevel?",
                attend_status=AttendStatus.ON_WAIT_LIST,
            )

    def get_attendee(self, data: dict):
        username: str = data.get("username")
        rfid: str = data.get("rfid")
        event_id: int = data.get("event")
        user = User.objects.get(Q(username=username) | Q(rfid=rfid, rfid__isnull=False))
        return Attendee.objects.get(user=user, event_id=event_id)

    def validate(self, attrs: dict):
        admin_user: User = self.context.get("request").user
        username: str = attrs.get("username")
        rfid: str = attrs.get("rfid")
        event_id: int = attrs.get("event")
        waitlist_approved: bool = attrs.get("approved")

        self._validate_rfid(rfid)
        self._validate_username(username)
        self._validate_event(event_id)

        if not admin_user.is_authenticated:
            raise RegisterAttendanceError(
                detail="Administerende bruker må være logget inn for å registrere oppmøte",
                attend_status=AttendStatus.NOT_LOGGED_IN,
            )

        if not (username or rfid):
            raise RegisterAttendanceError(
                detail="Mangler både RFID og brukernavn. Vennligst prøv igjen.",
                attend_status=AttendStatus.USERNAME_AND_RFID_MISSING,
            )

        if username and rfid:
            try:
                user = User.objects.get(username=username)
                user.rfid = rfid
                user.save()
                logger.debug(
                    f'Storing new RFID to user "{user}"',
                    extra={"user": user.pk, "rfid": rfid},
                )
            except (IntegrityError, ValidationError):
                logger.error(
                    f'Could not store RFID information for username "{username}" with RFID "{rfid}".'
                )
                raise RegisterAttendanceError(
                    detail="Det oppstod en feil da vi prøvde å lagre informasjonen. Vennligst prøv igjen. "
                    "Dersom problemet vedvarer, ta kontakt med dotkom. "
                    "Personen kan registreres med brukernavn i steden for RFID.",
                    attend_status=AttendStatus.REGISTER_ERROR,
                )

        try:
            attendee = self.get_attendee(attrs)
            self._handle_attendee(attendee, waitlist_approved)
        except Attendee.DoesNotExist:
            raise RegisterAttendanceError(
                detail="Brukeren er ikke påmeldt dette arrangementet",
                attend_status=AttendStatus.USER_NOT_ATTENDING,
            )
        except User.DoesNotExist:
            # If attendee tried to attend by a username that isn't tied to a user
            if not rfid:
                raise RegisterAttendanceError(
                    detail="Brukernavnet finnes ikke. Husk at det er et online.ntnu.no brukernavn! "
                    "(Prøv igjen, eller scan nytt kort for å avbryte.)",
                    attend_status=AttendStatus.USERNAME_DOES_NOT_EXIST,
                )

            # If attendee tried to attend by card, but card isn't tied to a user
            else:
                raise RegisterAttendanceError(
                    detail="Kortet finnes ikke i databasen. Skriv inn et online.ntnu.no brukernavn for å "
                    "knytte kortet til brukeren og registrere oppmøte.",
                    attend_status=AttendStatus.RFID_DOES_NOT_EXIST,
                )

        return attrs
