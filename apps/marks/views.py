from rest_framework import mixins, permissions, viewsets

from apps.marks.models import MarkUser, Suspension
from apps.marks.serializers import MarkUserSerializer, SuspensionSerializer


class MarksViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = MarkUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        user_marks = MarkUser.objects.filter(user=user)
        return user_marks


class SuspensionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SuspensionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Suspension.objects.filter(user=self.request.user)
