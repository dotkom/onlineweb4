from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.viewsets import ModelViewSet

from apps.api.permissions import TokenHasScopeOrUserHasModelPermissionsOrWriteOnly
from apps.approval.models import CommitteeApplication, CommitteeApplicationPeriod

from .filters import CommitteeApplicationPeriodFilter
from .serializers import (
    CommitteeApplicationPeriodSerializer,
    CommitteeApplicationSerializer,
)


class CommitteeApplicationPeriodViewSet(ModelViewSet):
    serializer_class = CommitteeApplicationPeriodSerializer
    queryset = CommitteeApplicationPeriod.objects.all()
    filter_class = CommitteeApplicationPeriodFilter
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class CommitteeApplicationViewSet(ModelViewSet):
    """
    It's possible for anyone to POST to this view, but to access the objects you need a bearer token
    with the required scope.
    """

    serializer_class = CommitteeApplicationSerializer
    queryset = CommitteeApplication.objects.all()
    permission_classes = [TokenHasScopeOrUserHasModelPermissionsOrWriteOnly]

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(applicant=self.request.user)
        else:
            serializer.save()
