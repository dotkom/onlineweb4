from rest_framework import mixins, permissions, viewsets

from apps.notifications.models import (
    Notification,
    Permission,
    Subscription,
    UserPermission,
)
from apps.notifications.serializers import (
    NotificationSerializer,
    PermissionSerializer,
    SubscriptionSerializer,
    UserPermissionSerializer,
)


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        return queryset.filter(recipient=user)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()


class UserPermissionViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserPermissionSerializer
    queryset = UserPermission.objects.all()

    def get_queryset(self):
        user = self.request.user
        UserPermission.create_all_for_user(user)
        queryset = super().get_queryset()
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
