# -*- encoding: utf-8 -*-
from django import forms

from apps.article.models import Tag, Article
from apps.dashboard.widgets import DatetimePickerInput, widget_generator
from apps.gallery.widgets import SingleImageInput


class TagForm(forms.ModelForm):

    class Meta(object):
        model = Tag
        fields = ['name', 'slug']


class ArticleForm(forms.ModelForm):

    class Meta(object):
        """
        Add fields that should have DTP activated in the datetimepicker_fields list
        """

        model = Article
        exclude = ['old_image']

        # Fields should be a mapping between field name and an attribute dictionary
        img_fields = [('image', {'id': 'responsive-image-id'})]
        dtp_fields = [('published_date', {})]

        widgets = {}

        for field, widget in widget_generator(SingleImageInput, img_fields).items():
            widgets[field] = widget
        for field, widget in widget_generator(DatetimePickerInput, dtp_fields).items():
            widgets[field] = widget
