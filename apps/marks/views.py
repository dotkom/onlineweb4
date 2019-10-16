from rest_framework import mixins, permissions, viewsets

from apps.marks.models import MarkRuleSet, MarkUser, RuleAcceptance, Suspension
from apps.marks.serializers import (
    MarkRuleSetReadOnlySerializer,
    MarkUserSerializer,
    RuleAcceptanceCreateSerializer,
    RuleAcceptanceReadOnlySerializer,
    SuspensionSerializer,
)


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


class MarkRuleSetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MarkRuleSetReadOnlySerializer
    permission_classes = (permissions.AllowAny,)
    queryset = MarkRuleSet.objects.all()


class RuleAccpetanceViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = RuleAcceptance.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RuleAcceptanceReadOnlySerializer
        if self.action == 'create':
            return RuleAcceptanceCreateSerializer

        return super().get_serializer_class()
