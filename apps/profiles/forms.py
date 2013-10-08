# -*- coding: utf-8 -*-

from django import forms

from apps.profiles.models import Privacy
from apps.authentication.models import OnlineUser

class ProfileForm(forms.ModelForm):

    class Meta:
        model = OnlineUser

        fields = ['nickname', 'website', 'phone_number', 'address', 'zip_code', 'allergies', 'mark_rules', ]
        widgets = {
            'allergies' : forms.Textarea(attrs={'id' : 'allergies'}),
        }

class ImageForm(forms.ModelForm):

    class Meta:
        model = OnlineUser

        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class' : 'hidden-input', 'id' : 'image'}),
        }

class PrivacyForm(forms.ModelForm):

    class Meta:
        model = Privacy
        exclude = ['user']


class MailSettingsForm(forms.ModelForm):

    class Meta:
        model = OnlineUser

        fields = ['email', 'infomail', ]