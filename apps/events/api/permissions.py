from django.utils import timezone
from rest_framework import permissions

from apps.authentication.models import OnlineUser as User

from ..models import AttendanceEvent, Attendee


class RegisterPermission(permissions.IsAuthenticated):
    """
    Check if a user has permission to register for an attendance event.
    """

    message = ""

    def has_object_permission(self, request, view, obj: AttendanceEvent):
        attend_response = obj.is_eligible_for_signup(request.user)
        can_attend = attend_response.get("status")
        self.message = attend_response.get("message")
        return can_attend


class UnregisterPermission(permissions.IsAuthenticated):
    """
    Check if a user has permission to unregister from an attendance event.
    """

    message = ""

    @staticmethod
    def _is_user_attending(attendance_event: AttendanceEvent, user: User):
        return attendance_event.is_attendee(user)

    @staticmethod
    def _has_deadline_passed(attendance_event: AttendanceEvent, user: User) -> bool:
        """ User can only be unattended before the deadline, or if they are on the wait list. """
        now = timezone.now()
        return (
            now > attendance_event.unattend_deadline
            and not attendance_event.is_on_waitlist(user)
        )

    @staticmethod
    def _has_event_started(attendance_event: AttendanceEvent):
        return attendance_event.event.event_start < timezone.now()

    @staticmethod
    def _user_has_paid(attendance_event: AttendanceEvent, user: User):
        attendee = Attendee.objects.get(event=attendance_event, user=user)
        return attendee.has_paid

    def has_object_permission(self, request, view, obj: AttendanceEvent):
        user = request.user

        if not self._is_user_attending(obj, user):
            self.message = "Du er ikke påmeldt dette arrangementet."
            return False

        if self._has_deadline_passed(obj, user):
            self.message = "Avmeldingsfristen har gått ut, det er ikke lenger mulig å melde seg av arrangementet."
            return False

        if self._has_event_started(obj):
            self.message = (
                "Du kan ikke melde deg av et arrangement som allerede har startet."
            )
            return False

        if self._user_has_paid(obj, user):
            self.message = "Du må refundere betalingene dine før du kan melde deg av."
            return False

        return True


class ChangeAttendeePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Attendee):
        return request.user == obj.user
