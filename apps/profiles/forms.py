# -*- coding: utf-8 -*-

from django import forms

from apps.profiles.models import Privacy
from apps.authentication.models import OnlineUser

class ProfileForm(forms.ModelForm):

    class Meta:
        model = OnlineUser
        fields = ['email', 'nickname', 'website', 'phone_number', 'address', 'zip_code', 'allergies', 'infomail', 'mark_rules', ]
        widgets = {
            'allergies' : forms.Textarea(attrs={'id' : 'allergies'})
        }


class PrivacyForm(forms.ModelForm):

    class Meta:
        model = Privacy
        exclude = ['user']