# -*- coding: utf-8 -*-

import re

from django import forms
from django.contrib import auth
from django.utils.translation import ugettext as _

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Email


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(), label=_("Brukernavn"), max_length=50)
    password = forms.CharField(widget=forms.PasswordInput(), label=_("Passord"))
    user = None

    def clean(self):
        if self._errors:
            return

        username = self.cleaned_data['username'].lower()

        if '@' in username:
            email = Email.objects.filter(email=username)
            if email:
                username = email[0].user.username

        user = auth.authenticate(username=username, password=self.cleaned_data['password'])

        if user:
            if user.is_active:
                self.user = user
            else:
                self._errors['username'] = self.error_class(
                    [_("Din konto er ikke aktiv. Forsøk gjenoppretning av passord.")]
                )
        else:
            # This error will also be produced if the email supplied does not exist.
            self._errors['username'] = self.error_class(
                [_("Kontoen eksisterer ikke, eller kombinasjonen av brukernavn og passord er feil.")]
            )
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            auth.login(request, self.user)
            return True
        return False


class RegisterForm(forms.Form):
    username = forms.CharField(
        label=_("Brukernavn"),
        max_length=20,
        help_text='Valgfritt brukernavn. (Konverteres automatisk til små bokstaver.)'
    )
    first_name = forms.CharField(
        label=_("Fornavn"),
        max_length=50,
        help_text='Mellomnavn inkluderer du etter fornavnet ditt'
    )
    last_name = forms.CharField(label=_("Etternavn"), max_length=50)
    email = forms.EmailField(
        label=_("Epost"),
        max_length=50,
        help_text='Du kan legge til flere epostadresser senere i din profil.'
    )
    password = forms.CharField(widget=forms.PasswordInput(), label=_("Passord"))
    repeat_password = forms.CharField(widget=forms.PasswordInput(), label=_("Gjenta passord"))
    address = forms.CharField(
        label=_("Adresse"),
        max_length=100,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )
    zip_code = forms.CharField(
        label=_("Postnummer"),
        max_length=4,
        required=False,
        help_text='Vi henter by basert på postnummer'
    )
    phone = forms.CharField(label=_("Telefon"), max_length=20, required=False)

    def clean(self):
        super(RegisterForm, self).clean()
        if self.is_valid():
            cleaned_data = self.cleaned_data

            # Check passwords
            if cleaned_data['password'] != cleaned_data['repeat_password']:
                self._errors['repeat_password'] = self.error_class([_("Passordene er ikke like.")])

            # Check username
            username = cleaned_data['username'].lower()
            if User.objects.filter(username=username).count() > 0:
                self._errors['username'] = self.error_class([_("Brukernavnet er allerede registrert.")])
            if not re.match("^[a-zA-Z0-9_-]+$", username):
                self._errors['username'] = self.error_class([
                    _("Ditt brukernavn inneholdt ulovlige tegn. Lovlige tegn: a-Z 0-9 - _")
                ])

            # Check email
            email = cleaned_data['email'].lower()
            if Email.objects.filter(email=email).count() > 0:
                self._errors['email'] = self.error_class([_(
                    "Det eksisterer allerede en bruker med denne epostadressen."
                )])

            # Check if it's studmail and if someone else already has it in their profile
            if re.match(r'[^@]+@stud\.ntnu\.no', email):
                ntnu_username = email.split("@")[0]
                user = User.objects.filter(ntnu_username=ntnu_username)
                if user.count() == 1:
                    self._errors['email'] = self.error_class([
                        _("En bruker med dette NTNU-brukernavnet eksisterer allerede.")
                    ])

            # ZIP code digits only
            zip_code = cleaned_data['zip_code']
            if len(zip_code) != 0:
                # Check if zip_code is 4 digits long
                if not re.match(r'\d{4}', zip_code):
                    self._errors['zip_code'] = self.error_class([_("Postnummer må bestå av fire siffer.")])

            return cleaned_data


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'username', 'nickname', 'first_name', 'last_name',
            'address', 'zip_code', 'ntnu_username', 'online_mail',
            'phone_number', 'rfid', 'started_date', 'website', 'github', 'linkedin',
            'bio', 'allergies', 'compiled', 'mark_rules', 'infomail', 'jobmail',
        )


class RecoveryForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50)


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(), label=_("Nytt passord"))
    repeat_password = forms.CharField(widget=forms.PasswordInput(), label=_("Gjenta passord"))

    def clean(self):
        super(ChangePasswordForm, self).clean()
        if self.is_valid():
            cleaned_data = self.cleaned_data

            # Check passwords
            if cleaned_data['new_password'] != cleaned_data['repeat_password']:
                self._errors['repeat_password'] = self.error_class([_("Passordene er ikke like.")])

            return cleaned_data


class NewEmailForm(forms.Form):
    new_email = forms.EmailField(label=_("ny epostadresse"))
