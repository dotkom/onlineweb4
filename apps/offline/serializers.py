from rest_framework import serializers
from apps.offline.models import Issue


class OfflineIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
                'description', 'id', 'issue', 'release_date', 'title',
            )
