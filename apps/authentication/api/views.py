from guardian.shortcuts import get_objects_for_user
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition
from apps.authentication.serializers import (EmailCreateSerializer, EmailReadOnlySerializer,
                                             EmailUpdateSerializer,
                                             PositionCreateAndUpdateSerializer,
                                             PositionReadOnlySerializer, SpecialPositionSerializer,
                                             UserCreateSerializer, UserReadOnlySerializer,
                                             UserUpdateSerializer)


class UserViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin):
    """
    Viewset for User serializer. Supports filtering on 'first_name', 'last_name', 'email'
    """
    permission_classes = (AllowAny,)
    filterset_fields = ('first_name', 'last_name', 'rfid',)

    def get_queryset(self):
        """
        Permitted users can view users they have permission for to view.
        Users can only update/delete their own users.
        """
        user = self.request.user

        if self.action in ['list', 'retrieve']:
            if not user.is_authenticated:
                return User.objects.none()
            if user.is_superuser:
                return User.objects.all()
            return get_objects_for_user(user, 'authentication.view_onlineuser')

        if self.action in ['list', 'retrieve', 'destroy']:
            return User.objects.filter(user=user)

        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        if self.action in ['list', 'retrieve']:
            return UserReadOnlySerializer

        return super().get_serializer_class()


class EmailViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Email.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return EmailCreateSerializer
        if self.action in ['update', 'partial_update']:
            return EmailUpdateSerializer
        if self.action in ['list', 'retrieve']:
            return EmailReadOnlySerializer

        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        instance: Email = self.get_object()
        if instance.primary:
            return Response({
                'message': 'Du kan ikke slette en primær-epost. Du må først velge en annen epost som '
                           'primær for å kunne slette denne.'
            }, status=status.HTTP_400_BAD_REQUEST)


class PositionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PositionCreateAndUpdateSerializer
        if self.action in ['list', 'retrieve']:
            return PositionReadOnlySerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        return Position.objects.filter(user=user)


class SpecialPositionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SpecialPositionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return SpecialPosition.objects.filter(user=user)
