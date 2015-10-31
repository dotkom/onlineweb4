# -*- coding: utf-8 -*-
import re

from django import forms
from django.utils.translation import ugettext as _

from apps.profiles.models import Privacy
from apps.authentication.models import OnlineUser, Position


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
            'linkedin'
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
        if len(zip_code) != 0 and (len(zip_code) != 4 or not zip_code.isdigit()):
            self._errors['zip_code'] = self.error_class([_(u"Postnummer må bestå av fire siffer.")])

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
                [_(u'Feil format. Dobbelsjekk at input er på formatet YYYY-YYYY.')]
            )
            return self.cleaned_data

        years = year_range.split('-')

        # If somewhat they fucked up input, we don't want None-shit after the split.
        if not years[0] or not years[1]:
            self._errors['period'] = self.error_class([_(u'Feil format. Dobbelsjekk input.')])
            return self.cleaned_data

        # If first year is larger than latter, or the diff is more than one, fail.
        if (int(years[0]) > int(years[1])) or (int(years[1]) - int(years[0])) > 1:
                self._errors['period'] = self.error_class([_(u'Ikke gyldig års-intervall. Bare ett år er tillat.')])

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
