from rest_framework import mixins, viewsets, permissions

from oidc_provider.models import Client, ResponseType, UserConsent

from .serializers import (ClientCreateAndUpdateSerializer, ClientReadOnlySerializer, ResponseTypeReadOnlySerializer,
                          UserConsentReadOnlySerializer,)


class UserConsentViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin):
    serializer_class = UserConsentReadOnlySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return UserConsent.objects.filter(user=user)


class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        if self.action in ['retrieve', 'list']:
            return Client.objects.all()
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            user = self.request.user
            if user.is_anonymous:
                return Client.objects.none()
            return Client.objects.filter(user=user)

        return super().get_queryset()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ClientReadOnlySerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ClientCreateAndUpdateSerializer

        return super().get_serializer_class()


class ResponseTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResponseTypeReadOnlySerializer
    permission_classes = (permissions.AllowAny,)
    queryset = ResponseType.objects.all()
