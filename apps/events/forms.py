#-*- coding: utf-8 -*-

from django import forms
from captcha.fields import CaptchaField
from django.utils.translation import ugettext as _

class CaptchaForm(forms.Form):

    phone_number = forms.CharField(label=_(u'Telefonnummer er påkrevd for å være påmeldt et arrangement.'),
                                   error_messages={'required' : _(u'Telefonnummer er påkrevd!')})
    mark_rules = forms.BooleanField(label=_(u'Jeg godtar <a href="/profile/#marks" target="_blank">prikkreglene</a>'),
                                    error_messages={'required' : _(u'Du må godta prikkereglene!')})
    captcha = CaptchaField(error_messages={'required' : _(u'Du klarte ikke captchaen! Er du en bot?')})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CaptchaForm, self).__init__(*args, **kwargs)

        # Removing mark rules field if user has already accepted the rules
        if self.user and self.user.is_authenticated():
            if self.user.mark_rules:
                del self.fields['mark_rules']

            if self.user.phone_number:
                del self.fields['phone_number']


    def clean(self):
        super(CaptchaForm, self).clean()
        cleaned_data = self.cleaned_data

        if 'mark_rules' in self.fields:
            if 'mark_rules' in cleaned_data:
                mark_rules = cleaned_data['mark_rules']

                if mark_rules:
                    self.user.mark_rules = True
                    self.user.save()

        if 'phone_number' in self.fields:
            if 'phone_number' in cleaned_data:
                phone_number = cleaned_data['phone_number']

                if phone_number:
                    self.user.phone_number = phone_number
                    self.user.save()

        return cleaned_data