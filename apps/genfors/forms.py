from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

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
