from rest_framework import viewsets

from apps.contribution.models import Repository
from apps.contribution.serializers import RepositorySerializer


class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    ordering = ('-updated_at',)
