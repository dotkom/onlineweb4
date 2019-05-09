from guardian.shortcuts import get_objects_for_user
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import (UserCreateSerializer, UserReadOnlySerializer,
                                             UserUpdateSerializer)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    Viewset for User serializer. Supports filtering on 'first_name', 'last_name', 'email'
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    filterset_fields = ('first_name', 'last_name', 'rfid',)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        if user.is_superuser or user.is_staff:
            return User.objects.all()
        return get_objects_for_user(user, 'authentication.view_online_user')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        if self.action in ['list', 'retrieve']:
            return UserReadOnlySerializer

        return super().get_serializer_class()
