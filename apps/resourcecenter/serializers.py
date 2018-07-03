from rest_framework import serializers

from apps.resourcecenter.models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('id', 'title', 'description', 'image')
