# -*- coding: utf-8 -*-

from django import forms

from apps.profiles.models import Privacy
from apps.authentication.models import OnlineUser

class ProfileForm(forms.ModelForm):

    # image_upload = forms.ImageField()
    # image_upload.widget.attrs["id"] = "hidden-input"

    class Meta:
        model = OnlineUser

        fields = ['email', 'nickname', 'website', 'phone_number', 'address', 'zip_code', 'allergies', 'infomail', 'mark_rules', 'image']
        widgets = {
            'allergies' : forms.Textarea(attrs={'id' : 'allergies'}),
            'image' : forms.FileInput(attrs={'id' : 'hidden-input'}),
        }


class PrivacyForm(forms.ModelForm):

    class Meta:
        model = Privacy
        exclude = ['user']