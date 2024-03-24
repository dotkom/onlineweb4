from rest_framework.permissions import (
    DjangoModelPermissions,
    DjangoModelPermissionsOrAnonReadOnly,
    IsAuthenticated,
)
from rest_framework.viewsets import ModelViewSet

from ..models import (
    CommitteeApplication,
    CommitteeApplicationPeriod,
    MembershipApproval,
)
from .filters import CommitteeApplicationPeriodFilter
from .serializers import (
    CommitteeApplicationPeriodSerializer,
    CommitteeApplicationSerializer,
    MembershipApprovalSerializer,
)


class UserHasModelPermissionsOrWriteOnly(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return super().has_permission(request, view)


class CommitteeApplicationPeriodViewSet(ModelViewSet):
    serializer_class = CommitteeApplicationPeriodSerializer
    queryset = CommitteeApplicationPeriod.objects.all()
    filterset_class = CommitteeApplicationPeriodFilter
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class CommitteeApplicationViewSet(ModelViewSet):
    """
    It's possible for anyone to POST to this view, but to access the objects you need a bearer token
    with the required scope.
    """

    serializer_class = CommitteeApplicationSerializer
    queryset = CommitteeApplication.objects.all()
    permission_classes = [UserHasModelPermissionsOrWriteOnly]

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(applicant=self.request.user)
        else:
            serializer.save()


class MembershipApprovalViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = MembershipApprovalSerializer

    def get_queryset(self):
        if not self.request.user:
            queryset = MembershipApproval.objects.none()
        else:
            queryset = MembershipApproval.objects.filter(applicant=self.request.user.id)

        return queryset
