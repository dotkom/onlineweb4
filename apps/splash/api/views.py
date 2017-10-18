from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.splash.api.serializers import SplashEventSerializer
from apps.splash.filters import SplashEventFilter
from apps.splash.models import SplashEvent


class HundredItemsPaginator(PageNumberPagination):
    page_size = 100


class SplashEventViewSet(ReadOnlyModelViewSet):
    queryset = SplashEvent.objects.all()
    serializer_class = SplashEventSerializer
    pagination_class = HundredItemsPaginator
    filter_class = SplashEventFilter
    filter_fields = ('start_time', 'end_time')
    ordering_fields = ('id', 'start_time', 'end_time')
