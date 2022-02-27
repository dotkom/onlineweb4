from django.contrib.auth.models import Group, Permission
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.authentication.models import Email, GroupMember, GroupRole, OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition
from apps.authentication.serializers import (
    AnonymizeUserSerializer,
    EmailCreateSerializer,
    EmailReadOnlySerializer,
    EmailUpdateSerializer,
    GroupMemberCreateSerializer,
    GroupMemberReadOnlySerializer,
    GroupMemberUpdateSerializer,
    GroupReadOnlySerializer,
    GroupRoleReadOnlySerializer,
    OnlineGroupCreateOrUpdateSerializer,
    OnlineGroupReadOnlySerializer,
    PasswordUpdateSerializer,
    PermissionReadOnlySerializer,
    PositionCreateAndUpdateSerializer,
    PositionReadOnlySerializer,
    SpecialPositionSerializer,
    UserCreateSerializer,
    UserReadOnlySerializer,
    UserUpdateSerializer,
)
from apps.common.rest_framework.mixins import MultiSerializerMixin
from apps.permissions.drf_permissions import DjangoObjectPermissionOrAnonReadOnly

from .filters import OnlineGroupFilter, UserFilter
from .permissions import IsSelfOrSuperUser
from .serializers.user_data import UserDataSerializer


class UserViewSet(
    MultiSerializerMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Viewset for User serializer. Supports filtering on 'first_name', 'last_name', 'email'
    """

    permission_classes = (IsSelfOrSuperUser,)
    filterset_class = UserFilter
    queryset = User.objects.all()
    serializer_classes = {
        "create": UserCreateSerializer,
        "update": UserUpdateSerializer,
        "read": UserReadOnlySerializer,
        "change_password": PasswordUpdateSerializer,
        "anonymize_user": AnonymizeUserSerializer,
        "dump_data": UserDataSerializer,
        "user_permissions": PermissionReadOnlySerializer,
    }

    @action(detail=True, methods=["put"])
    def change_password(self, request, pk=None):
        user: User = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["put"])
    def anonymize_user(self, request, pk=None):
        user: User = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="dump-data")
    def dump_data(self, request, pk: int):
        user: User = self.get_object()
        serializer = self.get_serializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="permissions")
    def user_permissions(self, request, pk):
        """
        Returns all permissions for a given user.
        Codename is "action_object", e.g. "delete_profile".
        Content_type is ID of object type.
        If you want to group permissions, you can group on object type and map the ID to the object from the codename string.
        """
        user = self.get_object()
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


class EmailViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_classes = {
        "create": EmailCreateSerializer,
        "update": EmailUpdateSerializer,
        "read": EmailReadOnlySerializer,
    }

    def get_queryset(self):
        return Email.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance: Email = self.get_object()
        if instance.primary:
            return Response(
                {
                    "message": "Du kan ikke slette en primær-epost. Du må først velge en annen epost som "
                    "primær for å kunne slette denne."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


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
        users = group.members.all()
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
