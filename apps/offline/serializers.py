from rest_framework import serializers

from apps.gallery.serializers import ResponsiveImageSerializer
from apps.offline.models import Issue


class OfflineIssueSerializer(serializers.ModelSerializer):
    image = ResponsiveImageSerializer()

    class Meta:
        model = Issue
        fields = (
            'description', 'id', 'issue', 'release_date', 'title', 'image',
        )
