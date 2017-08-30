# -*- coding: utf-8 -*-
import re

from django import forms
from django.contrib import auth
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser, Position
from apps.profiles.models import Privacy


class ProfileForm(forms.ModelForm):
    class Meta(object):
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
            'linkedin',
            'cardnumber',
            'rfid'
        ]
        widgets = {
            'allergies': forms.Textarea(attrs={'id': 'allergies'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'id': 'gender'}),
            'bio': forms.Textarea(attrs={'id': 'bio'}),
            'compiled': forms.CheckboxInput(attrs={'id': 'compiled'}),
        }

    def clean(self):
        super(ProfileForm, self).clean()

        cleaned_data = self.cleaned_data

        # ZIP code digits only
        zip_code = cleaned_data['zip_code']
        if len(zip_code) != 0 and not re.match(r'\d{4}', zip_code):
            self._errors['zip_code'] = self.error_class([_("Postnummer må bestå av fire siffer.")])

        # RFID code digits only
        rfid = cleaned_data['rfid']
        if len(rfid) != 0 and not re.match("(^\d{7}$)|(^\d{10}$)", rfid):
            self._errors['rfid'] = self.error_class([_("RFID må bestå av syv eller ti siffer.")])

        # Number on card
        cardnumber = cleaned_data['cardnumber']

        return cleaned_data

class PrivacyForm(forms.ModelForm):
    class Meta(object):
        model = Privacy
        exclude = ['user', 'expose_nickname']


class MailSettingsForm(forms.ModelForm):
    class Meta(object):
        model = OnlineUser
        fields = ['infomail', ]


class PositionForm(forms.ModelForm):
    class Meta(object):
        model = Position
        exclude = ['user']
        widgets = {
            'committee': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        super(PositionForm, self).clean()

        range_compiler = re.compile(r'\d{4}-\d{4}')
        year_range = self.cleaned_data['period']

        # If it doesn't match the format YYYY-YYYY
        if not range_compiler.match(year_range):
            self._errors['period'] = self.error_class(
                [_('Feil format. Dobbelsjekk at input er på formatet YYYY-YYYY.')]
            )
            return self.cleaned_data

        years = year_range.split('-')

        # If somewhat they fucked up input, we don't want None-shit after the split.
        if not years[0] or not years[1]:
            self._errors['period'] = self.error_class([_('Feil format. Dobbelsjekk input.')])
            return self.cleaned_data

        # If first year is larger than latter, or the diff is more than one, fail.
        if (int(years[0]) > int(years[1])) or (int(years[1]) - int(years[0])) > 1:
            self._errors['period'] = self.error_class([_('Ikke gyldig års-intervall. Bare ett år er tillat.')])

        return self.cleaned_data


class MembershipSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MembershipSettingsForm, self).__init__(*args, **kwargs)
        self.fields['started_date'].widget.attrs['class'] = 'hasDatePicker'

    class Meta(object):
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
