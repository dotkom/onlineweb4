# -*- encoding: utf-8 -*-
from django import forms

from apps.article.models import Article
from apps.dashboard.widgets import DatetimePickerInput, multiple_widget_generator
from apps.gallery.widgets import SingleImageInput

from taggit.forms import TagWidget


class ArticleForm(forms.ModelForm):
    class Meta(object):
        """
        Add fields that should have DTP activated in the datetimepicker_fields list
        """

        model = Article
        fields = [
            'heading',
            'ingress_short',
            'ingress',
            'content',
            'image',
            'video',
            'published_date',
            'authors',
            'tags',
            'featured'
        ]

        # Fields should be a mapping between field name and an attribute dictionary
        img_fields = [('image', {'id': 'responsive-image-id'})]
        dtp_fields = [('published_date', {})]
        widgetlist = [
            (DatetimePickerInput, dtp_fields),
            (SingleImageInput, img_fields)
        ]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)
        widgets.update({'tags': TagWidget(attrs={'placeholder': 'Eksempel: åre, online, kjelleren'})})
        labels = {
            'tags': u'Tags'
        }
