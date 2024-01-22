# -*- encoding: utf-8 -*-
from django import forms
from taggit.forms import TagWidget

from apps.article.models import Article
from apps.dashboard.widgets import DatetimePickerInput
from apps.gallery.constants import ImageFormat
from apps.gallery.widgets import SingleImageInput


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "heading",
            "ingress_short",
            "ingress",
            "content",
            "image",
            "video",
            "published_date",
            "authors",
            "tags",
            "featured",
        ]

        widgets = {
            "published_date": DatetimePickerInput(),
            "image": SingleImageInput(
                attrs={"id": "responsive-image-id", "preset": ImageFormat.ARTICLE}
            ),
            "tags": TagWidget(
                attrs={"placeholder": "Eksempel: åre, online, kjelleren"}
            ),
        }
        labels = {"tags": "Tags"}
