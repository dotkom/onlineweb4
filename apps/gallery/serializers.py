# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/18/15

from rest_framework import serializers

from apps.gallery.models import ResponsiveImage


class ResponsiveImageSerializer(serializers.ModelSerializer):1

    class Meta(object):
        model = ResponsiveImage
        fields = (
            'id', 'name', 'timestamp', 'description', 'thumb',
            'original', 'wide', 'lg', 'md', 'sm', 'xs', 'tags'
        )
