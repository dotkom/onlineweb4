from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.signing import Signer
from django.urls import reverse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.authentication.models import GroupMember, GroupRole, OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition
from apps.authentication.serializers import (
    AnonymizeUserSerializer,
    GroupMemberCreateSerializer,
    GroupMemberReadOnlySerializer,
    GroupMemberUpdateSerializer,
    GroupReadOnlySerializer,
    GroupRoleReadOnlySerializer,
    OnlineGroupCreateOrUpdateSerializer,
    OnlineGroupReadOnlySerializer,
    PermissionReadOnlySerializer,
    PositionCreateAndUpdateSerializer,
    PositionReadOnlySerializer,
    SpecialPositionSerializer,
    UserReadOnlySerializer,
    UserUpdateSerializer,
)
from apps.common.rest_framework.mixins import MultiSerializerMixin
from apps.permissions.drf_permissions import DjangoObjectPermissionOrAnonReadOnly

from .filters import OnlineGroupFilter, UserFilter
from .serializers.user_data import UserDataSerializer


class UserViewSet(
    MultiSerializerMixin,
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Viewset for User serializer. Supports filtering on 'first_name', 'last_name', 'email'
    """

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, UserReadOnlySerializer)

    permission_classes = (IsAuthenticated,)
    filterset_class = UserFilter
    queryset = User.objects.all()
    serializer_classes = {
        "update": UserUpdateSerializer,
        "read": UserReadOnlySerializer,
        "anonymize_user": AnonymizeUserSerializer,
        "dump_data": UserDataSerializer,
        "user_permissions": PermissionReadOnlySerializer,
    }

    # See templates/events/index.html. This is exposing this logic in the api.
    @action(detail=False, methods=["get"])
    def personalized_calendar_link(self, request):
        username = request.user.username
        signer = Signer()
        signed_value = signer.sign(username)

        link = settings.BASE_URL + reverse(
            "events_personal_ics", kwargs={"user": signed_value}
        )
        return Response(data={"link": link}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["put"])
    def anonymize_user(self, request):
        user: User = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="dump-data")
    def dump_data(self, request):
        user = request.user
        serializer = self.get_serializer(user)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="permissions")
    def user_permissions(self, request):
        """
        Returns all permissions for a given user.
        Codename is "action_object", e.g. "delete_profile".
        Content_type is ID of object type.
        If you want to group permissions, you can group on object type and map the ID to the object from the codename string.
        """
        user = request.user
        if user.is_superuser:
            permissions = Permission.objects.all().order_by("content_type")
        else:
            permissions = Permission.objects.filter(
                group__user=user
            ) | Permission.objects.filter(user=user)
            permissions.order_by("content_type").distinct()
        serializer = self.get_serializer(permissions, many=True)
        return Response(data=serializer.data)


class PermissionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint returns a dictionary of permissions for the authenticated user.
    This can be used to check whether a user should be able to perform a certain action related to an endpoint.
    """

    serializer_class = PermissionReadOnlySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            permissions = Permission.objects.all().order_by("content_type")
        else:
            permissions = Permission.objects.filter(
                group__user=user
            ) | Permission.objects.filter(user=user)
            permissions.distinct().order_by("content_type")
        return permissions


class PositionViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_classes = {
        "read": PositionReadOnlySerializer,
        "write": PositionCreateAndUpdateSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        return Position.objects.filter(user=user)


class SpecialPositionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SpecialPositionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return SpecialPosition.objects.filter(user=user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Group.objects.all()
    serializer_class = GroupReadOnlySerializer
    ordering = ("name",)


class OnlineGroupViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (DjangoObjectPermissionOrAnonReadOnly,)
    queryset = OnlineGroup.objects.all()
    filterset_class = OnlineGroupFilter
    serializer_classes = {
        "write": OnlineGroupCreateOrUpdateSerializer,
        "read": OnlineGroupReadOnlySerializer,
        "group_users": GroupMemberReadOnlySerializer,
    }

    @action(detail=True, methods=["get"], url_path="group-users")
    def group_users(self, request, pk: int = None):
        group: OnlineGroup = self.get_object()
        users = group.members.select_related("user").prefetch_related("roles")
        serializer = self.get_serializer(users, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class GroupMemberViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (DjangoObjectPermissionOrAnonReadOnly,)
    queryset = GroupMember.objects.all()
    serializer_classes = {
        "create": GroupMemberCreateSerializer,
        "update": GroupMemberUpdateSerializer,
        "read": GroupMemberReadOnlySerializer,
    }


class GroupRoleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = GroupRoleReadOnlySerializer
    queryset = GroupRole.objects.all()
