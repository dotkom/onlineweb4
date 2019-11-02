from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.splash.api.serializers import AudienceGroupSerializer, SplashEventSerializer
from apps.splash.filters import SplashEventFilter
from apps.splash.models import AudienceGroup, SplashEvent


class HundredItemsPaginator(PageNumberPagination):
    page_size = 100


class SplashEventViewSet(ReadOnlyModelViewSet):
    queryset = SplashEvent.objects.all()
    serializer_class = SplashEventSerializer
    pagination_class = HundredItemsPaginator
    filterset_class = SplashEventFilter
    filterset_fields = ("start_time", "end_time", "target_audience")
    ordering_fields = ("id", "start_time", "end_time")


class AudienceGroupViewSet(ReadOnlyModelViewSet):
    queryset = AudienceGroup.objects.all()
    serializer_class = AudienceGroupSerializer
    permission_classes = (AllowAny,)
