# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/18/15

from rest_framework import serializers

from apps.gallery.models import ResponsiveImage


class ResponsiveImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResponsiveImage
        fields = (
            'id', 'name', 'timestamp', 'description', 'thumb',
            'wide', 'lg', 'md', 'sm', 'xs'
        )
