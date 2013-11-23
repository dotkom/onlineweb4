# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from apps.profiles.models import Privacy
from apps.authentication.models import OnlineUser, FIELD_OF_STUDY_CHOICES

class ProfileForm(forms.ModelForm):

    class Meta:
        model = OnlineUser

        fields = ['nickname', 'website', 'phone_number', 'address', 'zip_code', 'allergies', 'gender', ]
        widgets = {
            'allergies' : forms.Textarea(attrs={'id' : 'allergies'}),
        }

    def clean(self):
        super(ProfileForm, self).clean()

        cleaned_data = self.cleaned_data

        # ZIP code digits only
        zip_code = cleaned_data['zip_code']
        if len(zip_code) != 0 and (len(zip_code) != 4 or not zip_code.isdigit()):
            self._errors['zip_code'] = self.error_class([_(u"Postnummer må bestå av fire siffer.")])

        return cleaned_data

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
        fields = ['infomail', ]


class MembershipSettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MembershipSettingsForm, self).__init__(*args, **kwargs)
        self.fields['started_date'].widget.attrs['class'] = 'hasDatePicker'

    class Meta:
        model = OnlineUser
        fields = ['field_of_study', 'started_date', ]

        widgets = {
            'started_date' : forms.TextInput(attrs={'placeholder' : 'YYYY-MM-DD'}),
        }
