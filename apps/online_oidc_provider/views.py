from django.conf import settings
from oidc_provider.models import Client, ResponseType, UserConsent
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.rest_framework.mixins import MultiSerializerMixin

from .serializers import (
    ClientCreateAndUpdateSerializer,
    ClientReadOnlySerializer,
    ClientReadOwnSerializer,
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
    ordering = ("-date_given",)

    def get_queryset(self):
        user = self.request.user
        return UserConsent.objects.filter(user=user)


class ClientViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_classes = {
        "read": ClientReadOnlySerializer,
        "write": ClientCreateAndUpdateSerializer,
    }
    ordering = ("-date_created",)
  #  required_scopes = ["oidcadmin"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [*super().get_permissions()]
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

    @action(
        detail=False,
        methods=["POST"],
        serializer_class=ClientReadOwnSerializer,
        permission_classes=[permissions.IsAuthenticated],
        url_path="get-own",
    )
    def get_own(self, request):
        """
        This methods uses POST since HTTPS POST encrypts the transmission
        and this endpoints transmits sensitive data.
        """
        if not request.is_secure() and not settings.DEBUG:
            return Response(
                data={"detail": "This endpoint requires HTTPS"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = self.request.user
        clients = Client.objects.filter(owner=user).order_by("id")
        page = self.paginate_queryset(clients)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(clients, many=True)
        return Response(serializer.data)


class ResponseTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResponseTypeReadOnlySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ResponseType.objects.all()
    ordering = ("id",)
