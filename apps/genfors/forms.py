from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _
from apps.genfors.models import Alternative, Meeting, Question


class LoginForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u"Passord"))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'autofocus': 'autofocus'})

    def clean(self):
        if self._errors:
            return
        if not hasattr(settings, 'GENFORS_ADMIN_PASSWORD'):
            self._errors['password'] = self.error_class([_(u"Admin passord har ikke blitt satt")])
        elif self.cleaned_data['password'] != settings.GENFORS_ADMIN_PASSWORD:
            self._errors['password'] = self.error_class([_(u"Feil passord")])
        return self.cleaned_data


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'start_date']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_type', 'anonymous', 'description']


class AlternativeForm(forms.ModelForm):
    class Meta:
        model = Alternative
        fields = ['description']


AlternativeFormSet = modelformset_factory(Alternative, form=AlternativeForm, extra=2, can_delete=True)


class RegisterVoterForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u"Pinkode"))

    def clean(self):
        if self._errors:
            return
        if not hasattr(settings, 'GENFORS_PIN_CODE'):
            self._errors['password'] = self.error_class([_(u'PIN-kode har ikke blitt satt')])
        elif self.cleaned_data['password'] != settings.GENFORS_PIN_CODE:
            self._errors['password'] = self.error_class([_(u'Feil PIN-kode')])
        return self.cleaned_data
