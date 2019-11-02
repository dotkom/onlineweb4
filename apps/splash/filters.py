import django_filters

from apps.splash.models import SplashEvent


class SplashEventFilter(django_filters.FilterSet):
    class Meta:
        model = SplashEvent
        fields = {
            "start_time": ["gte", "lte"],
            "end_time": ["gte", "lte"],
            "target_audience": ["exact"],
        }
