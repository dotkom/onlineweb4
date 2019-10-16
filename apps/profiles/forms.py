# -*- coding: utf-8 -*-
import re

from django import forms
from django.contrib import auth
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser, Position
from apps.profiles.models import Privacy

ZIP_CODE_VALIDATION_ERROR = "Postnummer må bestå av fire siffer."


class ProfileForm(forms.ModelForm):
    class Meta:
        model = OnlineUser

        fields = [
            'nickname',
            'website',
            'phone_number',
            'address',
            'zip_code',
            'allergies',
            'compiled',
            'bio',
            'gender',
            'github',
            'linkedin'
        ]
        widgets = {
            'allergies': forms.Textarea(attrs={'id': 'allergies'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'id': 'gender'}),
            'bio': forms.Textarea(attrs={'id': 'bio'}),
            'compiled': forms.CheckboxInput(attrs={'id': 'compiled'}),
        }

    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code']
        if not zip_code or not re.match(r'^\d{4}$', zip_code):
            self.add_error('zip_code', ZIP_CODE_VALIDATION_ERROR)

        return zip_code


class PrivacyForm(forms.ModelForm):
    class Meta:
        model = Privacy
        exclude = ['user', 'expose_nickname']


class MailSettingsForm(forms.ModelForm):
    class Meta:
        model = OnlineUser
        fields = ['infomail', ]


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        exclude = ['user']
        widgets = {
            'committee': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        super(PositionForm, self).clean()

        period_start = self.cleaned_data['period_start']
        period_end = self.cleaned_data['period_end']

        # Checks if period_start and period_end intervall is max one year.
        if (period_end - period_start).days > 365:
            self._errors['period_end'] = self.error_class([_('Du kan kun registrer verv i ett år av gangen.')])

        # Checks is period_start is a later date than period_end.
        if period_start > period_end:
            self._errors['period_start'] = self.error_class([_('Start-dato kan ikke være etter endt-dato.')])

        return self.cleaned_data


class MembershipSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MembershipSettingsForm, self).__init__(*args, **kwargs)
        self.fields['started_date'].widget.attrs['class'] = 'hasDatePicker'

    class Meta:
        model = OnlineUser
        fields = ['field_of_study', 'started_date']

        widgets = {
            'started_date': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        }


class InternalServicesForm(forms.Form):
    ow4_password = forms.CharField(widget=forms.PasswordInput(), label=_(u"Online passord"))
    services_password = forms.CharField(widget=forms.PasswordInput(), label=_(u"Ønsket service passord"))
    current_user = None

    def clean(self):
        super(InternalServicesForm, self).clean()
        if self.is_valid():
            cleaned_data = self.cleaned_data

            # User object relation here
            user = auth.authenticate(username=self.current_user.username, password=cleaned_data['ow4_password'])

            if user is None or user.id != self.current_user.id:
                self._errors['ow4_password'] = self.error_class([_(u"Passordet er ikke korrekt.")])

            return cleaned_data
