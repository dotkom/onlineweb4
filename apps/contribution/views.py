from rest_framework import viewsets

from apps.contribution.models import Repository
from apps.contribution.serializers import RepositorySerializer


def index(request):
    return


class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
