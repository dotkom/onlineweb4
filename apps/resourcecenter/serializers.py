from rest_framework import serializers

from apps.gallery.serializers import ResponsiveImageSerializer
from apps.resourcecenter.models import Resource


class ResourceSerializer(serializers.ModelSerializer):

    image = ResponsiveImageSerializer()

    class Meta:
        model = Resource
        fields = ('id', 'title', 'description', 'image')
