# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from apps.profiles.models import Privacy
from apps.authentication.models import OnlineUser

class ProfileForm(forms.ModelForm):

    class Meta:
        model = OnlineUser

        fields = ['nickname', 'website', 'phone_number', 'address', 'zip_code', 'allergies', 'mark_rules', 'image']
        widgets = {
            'allergies' : forms.Textarea(attrs={'id' : 'allergies'}),
            'image' : forms.FileInput(attrs={'id' : 'image', 'class' : 'hidden-input' }),
        }


class PrivacyForm(forms.ModelForm):

    class Meta:
        model = Privacy
        exclude = ['user']


class MailSettingsForm(forms.ModelForm):

    class Meta:
        model = OnlineUser

        fields = ['infomail', ]
