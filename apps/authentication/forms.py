# -*- coding: utf-8 -*-

import datetime
import re

from django import forms
from django.contrib import auth
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser as User

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(), label=_("Brukernavn"), max_length=50)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("Passord"))
    user = None

    def clean(self):
        if self._errors:
            return
    
        user = auth.authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])

        if user:
            if user.is_active:
                self.user = user
            else:
                self._errors['username'] = self.error_class([_("Din konto er ikke aktiv. Forsøk gjenoppretning av passord.")])
        else:
            self._errors['username'] = self.error_class([_("Kontoen eksisterer ikke, eller kombinasjonen av brukernavn og passord er feil.")])
        return self.cleaned_data

    def login(self, request):
        try:
            User.objects.get(username=request.POST['username'])
        except:
            return False
        if self.is_valid():
            auth.login(request, self.user)
            request.session.set_expiry(0)
            return True
        return False

class RegisterForm(forms.Form):
    username = forms.CharField(label=_("brukernavn"), max_length=20)
    first_name = forms.CharField(label=_("fornavn"), max_length=50)
    last_name = forms.CharField(label=_("etternavn"), max_length=50)
    email = forms.EmailField(label=_("epost"), max_length=50)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("passord"))
    repeat_password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("gjenta passord"))
    address = forms.CharField(label=_("adresse"), max_length=50)
    zip_code = forms.CharField(label=_("postnummer"), max_length=4)
    phone = forms.CharField(label=_("telefon"), max_length=20)
    
    def clean(self):
        super(RegisterForm, self).clean()
        if self.is_valid():
            cleaned_data = self.cleaned_data

            # Check passwords
            if cleaned_data['password'] != cleaned_data['repeat_password']:
                self._errors['repeat_password'] = self.error_class([_("Passordene er ikke like.")])

            # Check username
            username = cleaned_data['username']
            if User.objects.filter(username=username).count() > 0:
                self._errors['username'] = self.error_class([_("Brukernavnet er allerede registrert.")])
            if not re.match("^[a-zA-Z0-9_-]+$", username):
                self._errors['username'] = self.error_class([_("Ditt brukernavn inneholdt ulovlige tegn. Lovlige tegn: a-Z 0-9 - _")])

            # Check email
            email = cleaned_data['email']
            if User.objects.filter(email=email).count() > 0:
                self._errors['email'] = self.error_class([_("Det fins allerede en bruker med denne epostadressen.")])

            # ZIP code digits only
            zip_code = cleaned_data['zip_code']
            if len(zip_code) != 4 or not zip_code.isdigit():
                self._errors['zip_code'] = self.error_class([_("Postnummer må bestå av fire siffer.")])

            return cleaned_data 

class RecoveryForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50)

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("nytt passord"))
    repeat_password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("gjenta passord"))

    def clean(self):
        super(ChangePasswordForm, self).clean()
        if self.is_valid():
            cleaned_data = self.cleaned_data

            # Check passwords
            if cleaned_data['new_password'] != cleaned_data['repeat_password']:
                self._errors['repeat_password'] = self.error_class([_("Passordene er ikke like.")])

            return cleaned_data


class NewEmailForm(forms.Form):
    new_email = forms.EmailField(_(u"ny epostadresse"))
