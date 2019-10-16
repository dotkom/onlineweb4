from rest_framework import serializers

from apps.gallery.models import ResponsiveImage
from apps.gallery.serializers import ResponsiveImageSerializer
from apps.resourcecenter.models import Resource


class ResourceSerializer(serializers.ModelSerializer):

    image = ResponsiveImageSerializer(read_only=True)
    image_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='image',
        queryset=ResponsiveImage.objects.all()
    )

    class Meta:
        model = Resource
        fields = ('id', 'title', 'description', 'image', 'image_id', 'priority', 'active')
