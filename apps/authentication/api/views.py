from django.contrib.auth.models import Group
from guardian.shortcuts import get_objects_for_user
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
    PositionCreateAndUpdateSerializer,
    PositionReadOnlySerializer,
    SpecialPositionSerializer,
    UserCreateSerializer,
    UserReadOnlySerializer,
    UserUpdateSerializer,
)
from apps.common.rest_framework.mixins import MultiSerializerMixin

from .filters import UserFilter


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

    permission_classes = (AllowAny,)
    filterset_class = UserFilter
    serializer_classes = {
        "create": UserCreateSerializer,
        "update": UserUpdateSerializer,
        "read": UserReadOnlySerializer,
        "change_password": PasswordUpdateSerializer,
        "anonymize_user": AnonymizeUserSerializer,
    }

    def get_queryset(self):
        """
        Permitted users can view users they have permission for to view.
        Users can only update/delete their own users.
        """
        user = self.request.user

        if self.action in ["list", "retrieve"]:
            if not user.is_authenticated:
                return User.objects.none()
            if user.is_superuser:
                return User.objects.all()
            return get_objects_for_user(user, "authentication.view_onlineuser")

        if self.action in [
            "destroy",
            "update",
            "partial_update",
            "change_password",
            "anonymize_user",
        ]:
            return User.objects.filter(pk=user.id)

        return super().get_queryset()

    @action(detail=True, methods=["put"], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        user: User = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["put"], permission_classes=[IsAuthenticated])
    def anonymize_user(self, request, pk=None):
        user: User = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=None, status=status.HTTP_204_NO_CONTENT)


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


class OnlineGroupViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_classes = {
        "write": OnlineGroupCreateOrUpdateSerializer,
        "read": OnlineGroupReadOnlySerializer,
    }

    @staticmethod
    def get_editable_groups_for_user(user: User, action: str):
        if not user.is_authenticated:
            return OnlineGroup.objects.none()

        all_groups = OnlineGroup.objects.all()
        """ Updating or deleting requires admin rights or a leader role """
        if action in ["create", "update", "partial_update", "destroy"]:
            if user.is_superuser:
                return all_groups

            """ Group leaders or deputy leaders should be allowed to edit groups """
            allowed_group_ids = [
                group.id
                for group in all_groups
                if group.leader == user or group.deputy_leader == user
            ]
            return OnlineGroup.objects.filter(pk__in=allowed_group_ids)

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return OnlineGroup.objects.all()

        user = self.request.user
        return self.get_editable_groups_for_user(user, self.action)

    def create(self, request, *args, **kwargs):

        if request.user.is_superuser or request.user.has_perm(
            "authentication.add_onlinegroup"
        ):
            return super().create(request, *args, **kwargs)

        return Response(
            {"message": "Du har ikke tillatelse til å opprette grupper"},
            status=status.HTTP_403_FORBIDDEN,
        )


class GroupMemberViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_classes = {
        "create": GroupMemberCreateSerializer,
        "update": GroupMemberUpdateSerializer,
        "read": GroupMemberReadOnlySerializer,
    }

    @staticmethod
    def get_allowed_memberships_for_user(user: User, action: str):
        allowed_groups = OnlineGroupViewSet.get_editable_groups_for_user(user, action)
        allowed_membership_ids = []
        for group in allowed_groups:
            for membership in group.members.all():
                allowed_membership_ids.append(membership.id)

        return GroupMember.objects.filter(pk__in=allowed_membership_ids)

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return GroupMember.objects.all()

        user = self.request.user
        return self.get_allowed_memberships_for_user(user, self.action)

    def create(self, request, *args, **kwargs):

        if request.user.is_superuser or request.user.has_perm(
            "authentication.add_groupmember"
        ):

            return super().create(request, *args, **kwargs)

        return Response(
            {"message": "Du har ikke tillatelse til å opprette gruppemedlemskap"},
            status=status.HTTP_403_FORBIDDEN,
        )


class GroupRoleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = GroupRoleReadOnlySerializer
    queryset = GroupRole.objects.all()
