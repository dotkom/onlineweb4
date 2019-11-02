from rest_framework.serializers import ModelSerializer

from apps.splash.models import AudienceGroup, SplashEvent


class SplashEventSerializer(ModelSerializer):
    class Meta:
        model = SplashEvent
        fields = (
            "id",
            "title",
            "content",
            "start_time",
            "end_time",
            "target_audience",
            "event",
        )


class AudienceGroupSerializer(ModelSerializer):
    class Meta:
        model = AudienceGroup
        fields = ("id", "name")
