# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/18/15

from tastypie.resources import ModelResource

from apps.gallery.models import ResponsiveImage


class ImageResource(ModelResource):

    class Meta(object):
        queryset = ResponsiveImage.objects.all()
        resource_name = 'image'
        fields = [
            'name',
            'description',
            'timestamp',
            'image_original',
            'image_thumbnail',
            'image_wide',
            'image_lg',
            'image_md',
            'image_sm',
            'image_xs'
        ]
