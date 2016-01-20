# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import FormActions, Field, StrictButton, FieldWithButtons

from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _
from django.utils import timezone
from apps.genfors.models import Alternative, Meeting, Question

import datetime


class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label=_("Passord"))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'autofocus': 'autofocus'})

    def clean(self):
        if self._errors:
            return
        if not hasattr(settings, 'GENFORS_ADMIN_PASSWORD'):
            self._errors['password'] = self.error_class([_("Admin passord har ikke blitt satt")])
        elif self.cleaned_data['password'] != settings.GENFORS_ADMIN_PASSWORD:
            self._errors['password'] = self.error_class([_("Feil passord")])
        return self.cleaned_data


class MeetingForm(forms.ModelForm):
    helper = FormHelper()
    helper.layout = Layout(
        'title',
        Field('start_date', data_date_format="DD.MM.YY HH:mm "),
        FormActions(
            Submit('create', _('Opprett nytt møte'), css_class="btn-success"),
        )
    )

    class Meta:
        model = Meeting
        fields = ['title', 'start_date']

    def clean_start_date(self):
        date = self.cleaned_data['start_date']
        if date.date() < datetime.date.today():
            raise forms.ValidationError(_('Datoen må være i dag eller senere'))
        return date


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['description', 'anonymous', 'only_show_winner', 'majority_type', 'question_type']


class AlternativeForm(forms.ModelForm):
    helper = FormHelper()
    button = StrictButton('<span class="glyphicon glyphicon-remove"></span>', data_formset_delete_button='')
    helper.layout = Layout(
        'id',
        Field('DELETE', wrapper_class='hidden'),
        FieldWithButtons('description', button)
    )
    helper.form_tag = False

    class Meta:
        model = Alternative
        fields = ['description']


AlternativeFormSet = modelformset_factory(Alternative, form=AlternativeForm, can_delete=True, extra=0)


class RegisterVoterForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label=_("Pinkode"),
        help_text='Kode oppgitt under generalforsamling'
    )
    salt = forms.CharField(
        widget=forms.PasswordInput(),
        label=_('Personlig kode'),
        help_text=_(
            """Personlig kode brukes for å lage en unik hash som brukes til hemmelige valg.
            Denne lagres ikke og det er derfor ytterst viktig at du ikke glemmer den."""
        )
    )
    salt2 = forms.CharField(widget=forms.PasswordInput(), label=_('Gjenta personlig kode'))

    @staticmethod
    def get_active_meeting():
        today = datetime.date.today()
        hour24 = datetime.timedelta(hours=24)
        meetings = Meeting.objects.filter(
            start_date__lte=timezone.now(),
            ended=False,
            start_date__range=[today - hour24, today + hour24]
        ).order_by('-start_date')

        if meetings:
            return meetings[0]

    def clean(self):
        if self._errors:
            return
        elif self.cleaned_data['password'] != self.get_active_meeting().pin:
            self._errors['password'] = self.error_class([_('Feil PIN-kode')])
        elif self.cleaned_data['salt'] != self.cleaned_data['salt2']:
            self._errors['salt'] = self.error_class([_('De personlige kodene er ikke like')])
        return self.cleaned_data
