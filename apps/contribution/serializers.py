from rest_framework import serializers

from apps.contribution.models import Repository


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ('id', 'name', 'description', 'url', 'updated_at')
