#
# Created by 'myth' on 10/18/15

from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from apps.gallery.models import ResponsiveImage


class ResponsiveImageSerializer(TaggitSerializer, serializers.ModelSerializer):
    preset_display = serializers.CharField(source="get_preset_display")
    tags = TagListSerializerField()

    class Meta:
        model = ResponsiveImage
        fields = (
            "id",
            "name",
            "timestamp",
            "description",
            "thumb",
            "original",
            "wide",
            "lg",
            "md",
            "sm",
            "xs",
            "tags",
            "photographer",
            "preset",
            "preset_display",
        )
