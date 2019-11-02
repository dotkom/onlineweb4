import logging

from rest_framework import mixins, permissions, request, viewsets
from wiki import models

from apps.wiki_api.serializers import URLPathReadOnlySerializer

logger = logging.getLogger(__name__)


class WikiViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin
):
    permission_classes = (permissions.AllowAny,)
    queryset = models.URLPath.objects.all()
    serializer_class = URLPathReadOnlySerializer

    def get_object(self):
        path = self.request.path[13:-1]
        try:
            urlpath: models.URLPath = models.URLPath.get_by_path(
                path, select_related=True
            )
            return urlpath
        except models.URLPath.DoesNotExist:
            raise request.exceptions.NotFound
