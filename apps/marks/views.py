from rest_framework import mixins, permissions, viewsets

from apps.marks.models import Mark, MarkUser, Suspension
from apps.marks.serializers import MarkSerializer, SuspensionSerializer


class MarksViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = MarkSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        user_relation = MarkUser.objects.filter(user=user)
        mark_ids = [relation.mark.id for relation in user_relation]
        return Mark.objects.filter(pk__in=mark_ids)

class SuspensionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = SuspensionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Suspension.objects.filter(user=self.request.user)
