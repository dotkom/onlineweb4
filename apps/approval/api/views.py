from oauth2_provider.ext.rest_framework import OAuth2Authentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.viewsets import ModelViewSet

from apps.api.permissions import TokenHasScopeOrUserHasObjectPermissionsOrWriteOnly
from apps.approval.api.serializers import CommitteeApplicationSerializer
from apps.approval.models import CommitteeApplication


class CommitteeApplicationViewSet(ModelViewSet):
    """
    It's possible for anyone to POST to this view, but to access the objects you need a bearer token
    with the required scope.
    """
    serializer_class = CommitteeApplicationSerializer
    queryset = CommitteeApplication.objects.all()
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [TokenHasScopeOrUserHasObjectPermissionsOrWriteOnly]
    required_scopes = ['approval']

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(applicant=self.request.user)
        else:
            serializer.save()
