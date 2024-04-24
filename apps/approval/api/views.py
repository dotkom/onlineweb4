from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from ..models import MembershipApproval
from .serializers import MembershipApprovalSerializer


class MembershipApprovalViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = MembershipApprovalSerializer

    def get_queryset(self):
        if not self.request.user:
            queryset = MembershipApproval.objects.none()
        else:
            queryset = MembershipApproval.objects.filter(applicant=self.request.user.id)

        return queryset
