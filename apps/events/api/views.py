from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_objects_for_user
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.events.models.Attendance import DeregistrationFeedback
from apps.events.serializers import DeregisterFeedbackSerializer
from apps.payment.serializers import PaymentReadOnlySerializer
from apps.profiles.models import Privacy

from ..constants import AttendStatus
from ..filters import (
    EventFilter,
    ExtrasFilter,
    FieldOfStudyRuleFilter,
    GradeRuleFilter,
    RuleBundleFilter,
    UserGroupRuleFilter,
)
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
from ..utils import handle_attend_event_payment
from .permissions import (
    ChangeAttendeePermission,
    RegisterPermission,
    UnregisterPermission,
)
from .register_attendance_serializer import RegisterAttendanceSerializer
from .serializers import (
    AttendanceEventSerializer,
    AttendeeAdministrateSerializer,
    AttendeeSerializer,
    AttendeeUpdateSerializer,
    EventSerializer,
    ExtrasSerializer,
    FieldOfStudyRuleSerializer,
    GradeRuleSerializer,
    PublicAttendeeSerializer,
    RegisterSerializer,
    RuleBundleSerializer,
    UserGroupRuleSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = EventFilter
    ordering_fields = (
        "event_start",
        "event_end",
        "id",
        "closest",
        "has_passed",
        "attendance_event__registration_start",
        "attendance_event__registration_end",
    )
    ordering = ("has_passed", "closest", "id")

    def get_queryset(self):
        user = self.request.user
        return (
            Event.by_nearest_active_event.get_queryset_for_user(user)
            .select_related(
                "image",
                "organizer",
                "group_restriction",
                "attendance_event",
                "attendance_event__reserved_seats",
            )
            .prefetch_related("attendance_event__attendees")
        )


class AttendanceEventViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceEventSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    ordering_fields = ()

    def get_queryset(self):
        user = self.request.user
        events = Event.by_registration.get_queryset_for_user(user)
        return (
            AttendanceEvent.objects.all()
            .select_related("reserved_seats", "event")
            .prefetch_related("attendees__user")
            .filter(event__in=events)
        )

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=(permissions.IsAuthenticated, RegisterPermission),
        serializer_class=RegisterSerializer,
    )
    def register(self, request, pk=None):
        user = request.user
        privacy: Privacy = user.privacy
        attendance_event: AttendanceEvent = self.get_object()
        # Check if the recaptcha and other request data is valid
        register_serializer = self.get_serializer(data=request.data)
        register_serializer.is_valid(raise_exception=True)
        data = register_serializer.validated_data
        # Set the values to the users default settings if sent data is empty
        # intentionally uses that bool(None) == False
        attending_visibility = (
            specific
            if (specific := data.get("show_as_attending_event")) is not None
            else bool(privacy.visible_as_attending_events)
        )
        allow_pictures = (
            specific
            if (specific := data.get("allow_pictures")) is not None
            else bool(privacy.allow_pictures)
        )

        attendee = Attendee.objects.create(
            event=attendance_event,
            user=user,
            show_as_attending_event=attending_visibility,
            allow_pictures=allow_pictures,
            note=data.get("note"),
        )

        if attendance_event.payment():
            handle_attend_event_payment(attendance_event.event, user)

        attendee_serializer = AttendeeSerializer(attendee)
        return Response(data=attendee_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["DELETE"],
        permission_classes=(permissions.IsAuthenticated, UnregisterPermission),
        serializer_class=DeregisterFeedbackSerializer,
    )
    def unregister(self, request, pk=None):
        user = request.user
        attendance_event: AttendanceEvent = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        DeregistrationFeedback.objects.create(
            user=user,
            event=attendance_event.event,
            cause=serializer.validated_data.get("cause"),
            text=serializer.validated_data.get("text", ""),
        )

        attendee = Attendee.objects.get(event=attendance_event, user=user)
        # Attendees un-attend with themselves as the admin user.
        attendee.unattend(user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=PublicAttendeeSerializer,
        url_path="public-attendees",
    )
    def public_attendees(self, request, pk=None):
        attendance_event: AttendanceEvent = self.get_object()
        attendees = attendance_event.attending_attendees_qs
        serializer = self.get_serializer(attendees, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=PublicAttendeeSerializer,
        url_path="public-on-waitlist",
    )
    def public_on_waitlist(self, request, pk=None):
        attendance_event: AttendanceEvent = self.get_object()
        attendees = attendance_event.waitlist_qs
        serializer = self.get_serializer(attendees, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=AttendeeSerializer,
    )
    def attendee(self, request, pk=None):
        user = request.user
        attendance_event: AttendanceEvent = self.get_object()
        attendee = get_object_or_404(Attendee, event=attendance_event, user=user)
        serializer = self.get_serializer(attendee)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=ExtrasSerializer,
    )
    def extras(self, request, pk=None):
        attendance_event: AttendanceEvent = self.get_object()
        serializer = self.get_serializer(attendance_event.extras, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=PaymentReadOnlySerializer,
    )
    def payment(self, request, pk=None):
        attendance_event: AttendanceEvent = self.get_object()
        payment = attendance_event.get_payment()
        if not payment:
            raise NotFound
        serializer = self.get_serializer(payment)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AttendeeViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    serializer_class = AttendeeSerializer
    filterset_fields = (
        "event",
        "attended",
        "user",
        "show_as_attending_event",
        "allow_pictures",
        "extras",
    )

    @staticmethod
    def _get_allowed_attendees(user):
        """
        A user is allowed to see attendees for their own user, and for events they are organizing.
        """
        if user.is_anonymous:
            return Attendee.objects.none()

        attendees = get_objects_for_user(
            user, "events.change_attendee", accept_global_perms=False
        )
        attendees |= Attendee.objects.filter(user=user)
        return attendees.distinct()

    def get_queryset(self):
        return self._get_allowed_attendees(self.request.user)

    @action(
        detail=True,
        methods=["PATCH", "PUT"],
        permission_classes=(ChangeAttendeePermission,),
        serializer_class=AttendeeUpdateSerializer,
    )
    def change(self, request, pk=None):
        attendee: Attendee = self.get_object()
        partial = request.method == "PATCH"
        serializer = self.get_serializer(attendee, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["PATCH", "PUT"],
        permission_classes=(permissions.DjangoObjectPermissions,),
        serializer_class=AttendeeAdministrateSerializer,
    )
    def administrate(self, request, pk=None):
        attendee: Attendee = self.get_object()
        partial = request.method == "PATCH"
        serializer = self.get_serializer(attendee, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["POST"],
        serializer_class=RegisterAttendanceSerializer,
        url_path="register-attendance",
    )
    def register_attendance(self, request, pk=None):
        """
        Register that a user has physically attended an event.
        """
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        attendee = serializer.get_attendee(request.data)
        attendee.attended = True
        attendee.save()

        return Response(
            {
                "detail": {
                    "message": f"{attendee.user} er registrert som deltaker. Velkommen!",
                    "attend_status": AttendStatus.REGISTER_SUCCESS,
                    "attendee": attendee.id,
                }
            },
            status=status.HTTP_200_OK,
        )


class ExtrasViewSet(viewsets.ModelViewSet):
    serializer_class = ExtrasSerializer
    queryset = Extras.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = ExtrasFilter


class RuleBundleViewSet(viewsets.ModelViewSet):
    serializer_class = RuleBundleSerializer
    queryset = RuleBundle.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = RuleBundleFilter


class FieldOfStudyRuleViewSet(viewsets.ModelViewSet):
    serializer_class = FieldOfStudyRuleSerializer
    queryset = FieldOfStudyRule.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = FieldOfStudyRuleFilter


class GradeRuleViewSet(viewsets.ModelViewSet):
    serializer_class = GradeRuleSerializer
    queryset = GradeRule.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = GradeRuleFilter


class UserGroupRuleViewSet(viewsets.ModelViewSet):
    serializer_class = UserGroupRuleSerializer
    queryset = UserGroupRule.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = UserGroupRuleFilter
