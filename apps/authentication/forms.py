# -*- coding: utf-8 -*-

import datetime
import re

from django import forms
from django.contrib import auth
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser as User, Email

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(), label=_("Brukernavn"), max_length=50)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u"Passord"))
    user = None

    def clean(self):
        if self._errors:
            return

        self.cleaned_data['username'] = self.cleaned_data['username'].lower()
    
        user = auth.authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])

        if user:
            if user.is_active:
                self.user = user
            else:
                self._errors['username'] = self.error_class([_(u"Din konto er ikke aktiv. Forsøk gjenoppretning av passord.")])
        else:
            self._errors['username'] = self.error_class([_(u"Kontoen eksisterer ikke, eller kombinasjonen av brukernavn og passord er feil.")])
        return self.cleaned_data

    def login(self, request):
        try:
            User.objects.get(username=request.POST['username'])
        except:
            return False
        if self.is_valid():
            auth.login(request, self.user)
            return True
        return False

class RegisterForm(forms.Form):
    username = forms.CharField(label=_("Brukernavn"), max_length=20, help_text=u'Valgfritt brukernavn. (Konverteres automatisk til små bokstaver.)')
    first_name = forms.CharField(label=_("Fornavn"), max_length=50, help_text=u'Mellomnavn inkluderer du etter fornavnet ditt')
    last_name = forms.CharField(label=_("Etternavn"), max_length=50)
    email = forms.EmailField(label=_("Epost"), max_length=50, help_text=u'Du kan legge til flere epostadresser senere i din profil.')
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("Passord"))
    repeat_password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("Gjenta passord"))
    address = forms.CharField(label=_("Adresse"), max_length=100, required=False, widget=forms.Textarea(attrs={'rows':3}))
    zip_code = forms.CharField(label=_("Postnummer"), max_length=4, required=False, help_text=u'Vi henter by basert på postnummer')
    phone = forms.CharField(label=_("Telefon"), max_length=20, required=False)
    
    def clean(self):
        super(RegisterForm, self).clean()
        if self.is_valid():
            cleaned_data = self.cleaned_data

            # Check passwords
            if cleaned_data['password'] != cleaned_data['repeat_password']:
                self._errors['repeat_password'] = self.error_class([_(u"Passordene er ikke like.")])

            # Check username
            username = cleaned_data['username']
            if User.objects.filter(username=username).count() > 0:
                self._errors['username'] = self.error_class([_(u"Brukernavnet er allerede registrert.")])
            if not re.match("^[a-zA-Z0-9_-]+$", username):
                self._errors['username'] = self.error_class([_(u"Ditt brukernavn inneholdt ulovlige tegn. Lovlige tegn: a-Z 0-9 - _")])

            # Check email
            email = cleaned_data['email'].lower()
            if Email.objects.filter(email=email).count() > 0:
                self._errors['email'] = self.error_class([_(u"Det fins allerede en bruker med denne epostadressen.")])

            # ZIP code digits only
            zip_code = cleaned_data['zip_code']
            if len(zip_code) != 0:
                if len(zip_code) != 4 or not zip_code.isdigit():
                    self._errors['zip_code'] = self.error_class([_(u"Postnummer må bestå av fire siffer.")])

            return cleaned_data 

class RecoveryForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50)

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u"Nytt passord"))
    repeat_password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_(u"Gjenta passord"))

    def clean(self):
        super(ChangePasswordForm, self).clean()
        if self.is_valid():
            cleaned_data = self.cleaned_data

            # Check passwords
            if cleaned_data['new_password'] != cleaned_data['repeat_password']:
                self._errors['repeat_password'] = self.error_class([_(u"Passordene er ikke like.")])

            return cleaned_data


class NewEmailForm(forms.Form):
    new_email = forms.EmailField(label=_(u"ny epostadresse"))
