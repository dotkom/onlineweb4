from rest_framework.serializers import ModelSerializer

from apps.splash.models import SplashEvent


class SplashEventSerializer(ModelSerializer):

    class Meta:
        model = SplashEvent
        fields = (
            'id', 'title', 'content', 'start_time', 'end_time',
        )
