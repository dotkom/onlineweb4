# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/18/15

from apps.gallery.models import ResponsiveImage
from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField


class ResponsiveImageSerializer(TaggitSerializer, serializers.ModelSerializer):

    tags = TagListSerializerField()

    class Meta(object):
        model = ResponsiveImage
        fields = (
            'id', 'name', 'timestamp', 'description', 'thumb',
            'original', 'wide', 'lg', 'md', 'sm', 'xs', 'tags',
            'photographer'
        )
