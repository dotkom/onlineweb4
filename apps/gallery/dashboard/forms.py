# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from django import forms

from apps.gallery.models import ResponsiveImage


class ResponsiveImageForm(forms.ModelForm):

    class Meta(object):
        model = ResponsiveImage
        fields = ['name', 'description']
