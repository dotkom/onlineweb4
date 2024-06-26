#
# Created by 'myth' on 10/24/15

from django import forms
from taggit.forms import TagWidget

from apps.gallery.models import ResponsiveImage


class ResponsiveImageForm(forms.ModelForm):
    class Meta:
        model = ResponsiveImage
        fields = ["name", "description", "photographer", "tags", "preset"]
        widgets = {
            "tags": TagWidget(
                attrs={"placeholder": "Eksempel: kontoret, kjelleren, åre"}
            ),
            "photographer": forms.TextInput(
                attrs={"placeholder": "Eventuell(e) fotograf(er)..."}
            ),
        }
        labels = {"tags": "Tags"}
