from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_objects_for_user
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.payment.serializers import PaymentReadOnlySerializer

from ..constants import AttendStatus
from ..filters import EventFilter, ExtrasFilter
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
        "is_today",
        "registration_filtered",
    )
    ordering = ("-is_today", "registration_filtered", "id")

    def get_queryset(self):
        user = self.request.user
        return Event.by_registration.get_queryset_for_user(user)


class AttendanceEventViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceEventSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = AttendanceEvent.objects.all()

    def get_queryset(self):
        user = self.request.user
        events = Event.by_registration.get_queryset_for_user(user)
        return super().get_queryset().filter(event__in=events)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=(permissions.IsAuthenticated, RegisterPermission),
        serializer_class=RegisterSerializer,
    )
    def register(self, request, pk=None):
        user = request.user
        attendance_event: AttendanceEvent = self.get_object()
        # Check if the recaptcha and other request data is valid
        register_serializer = self.get_serializer(data=request.data)
        register_serializer.is_valid(raise_exception=True)

        data = register_serializer.validated_data
        attendee = Attendee.objects.create(
            event=attendance_event,
            user=user,
            show_as_attending_event=data.get("show_as_attending_event"),
            allow_pictures=data.get("allow_pictures"),
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
    )
    def unregister(self, request, pk=None):
        user = request.user
        attendance_event: AttendanceEvent = self.get_object()
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
        attendees = (
            attendance_event.attending_attendees_qs | attendance_event.waitlist_qs
        )
        attendees = attendees.order_by("-show_as_attending_event", "timestamp")
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
    filterset_fields = ("field_of_study_rules", "grade_rules", "user_group_rules")


class FieldOfStudyRuleViewSet(viewsets.ModelViewSet):
    serializer_class = FieldOfStudyRuleSerializer
    queryset = FieldOfStudyRule.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_fields = ("offset", "field_of_study")


class GradeRuleViewSet(viewsets.ModelViewSet):
    serializer_class = GradeRuleSerializer
    queryset = GradeRule.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_fields = ("offset", "grade")


class UserGroupRuleViewSet(viewsets.ModelViewSet):
    serializer_class = UserGroupRuleSerializer
    queryset = UserGroupRule.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_fields = ("offset", "group")
