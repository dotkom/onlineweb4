from oidc_provider.models import Client, ResponseType, UserConsent
from rest_framework import mixins, permissions, viewsets

from apps.common.rest_framework.mixins import MultiSerializerMixin

from .serializers import (
    ClientCreateAndUpdateSerializer,
    ClientReadOnlySerializer,
    ResponseTypeReadOnlySerializer,
    UserConsentReadOnlySerializer,
)


class UserConsentViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = UserConsentReadOnlySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return UserConsent.objects.filter(user=user)


class ClientViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_classes = {
        "read": ClientReadOnlySerializer,
        "write": ClientCreateAndUpdateSerializer,
    }

    def get_permissions(self):
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ["retrieve", "list"]:
            return Client.objects.all()
        if self.action in ["create", "update", "partial_update", "destroy"]:
            user = self.request.user
            if user.is_anonymous:
                return Client.objects.none()
            return Client.objects.filter(owner=user)

        return super().get_queryset()


class ResponseTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResponseTypeReadOnlySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ResponseType.objects.all()
