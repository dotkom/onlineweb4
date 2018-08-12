from rest_framework import serializers

from apps.resourcecenter.models import Resource
from apps.gallery.serializers import ResponsiveImageSerializer

class ResourceSerializer(serializers.ModelSerializer):

    image = ResponsiveImageSerializer()

    class Meta:
        model = Resource
        fields = ('id', 'title', 'description', 'image')
