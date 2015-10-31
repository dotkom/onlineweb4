# -*- coding: utf-8 -*-

import uuid
import re
from smtplib import SMTPException

from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters

# API v1
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from apps.authentication.serializers import UserSerializer

from apps.authentication.forms import (
    LoginForm,
    RegisterForm,
    RecoveryForm,
    ChangePasswordForm
)
from apps.authentication.models import OnlineUser as User, RegisterToken, Email


@sensitive_post_parameters()
def login(request):
    redirect_url = request.REQUEST.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.login(request):
            messages.success(request, _(u'Du er nå logget inn.'))
            if redirect_url:
                return HttpResponseRedirect(redirect_url)
            return HttpResponseRedirect('/')
        else:
            form = LoginForm(request.POST, auto_id=True)
    else:
        form = LoginForm()

    response_dict = {'form': form, 'next': redirect_url}
    return render(request, 'auth/login.html', response_dict)


def logout(request):
    auth.logout(request)
    messages.success(request, _(u'Du er nå logget ut.'))
    return HttpResponseRedirect('/')


@sensitive_post_parameters()
def register(request):
    if request.user.is_authenticated():
        messages.error(request, _(u'Registrering av ny konto krever at du er logget ut.'))
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                cleaned = form.cleaned_data

                # Create user
                user = User(
                    username=cleaned['username'],
                    first_name=cleaned['first_name'].title(),
                    last_name=cleaned['last_name'].title(),
                )
                # Set remaining fields
                user.phone_number = cleaned['phone']
                user.address = cleaned['address'].title()
                user.zip_code = cleaned['zip_code']
                # Store password properly
                user.set_password(cleaned['password'])
                # Users need to be manually activated
                user.is_active = False
                user.save()

                # Set email address
                email = Email(
                    user=user,
                    email=cleaned['email'].lower(),
                )
                email.primary = True
                email.save()

                # Create the registration token
                token = uuid.uuid4().hex
                rt = RegisterToken(user=user, email=email.email, token=token)
                rt.save()

                email_message = _(u"""
En konto har blitt registrert på online.ntnu.no med denne epostadressen. Dersom du ikke
har utført denne handlingen ber vi deg se bort fra denne eposten.

For å bruke denne kontoen kreves det at du verifiserer epostadressen. Du kan gjøre
dette ved å besøke linken under.

http://%s/auth/verify/%s/

Denne lenken vil være gyldig i 24 timer. Dersom du behøver å få tilsendt en ny lenke
kan dette gjøres med funksjonen for å gjenopprette passord.
""") % (request.META['HTTP_HOST'], token)
                try:
                    send_mail(_(u'Verifiser din konto'), email_message, settings.DEFAULT_FROM_EMAIL, [email.email, ])
                except SMTPException:
                    messages.error(request, u'Det oppstod en kritisk feil, epostadressen er ugyldig!')
                    return redirect('home')

                messages.success(
                    request,
                    _(u'Registreringen var vellykket. Se tilsendt epost for verifiseringsinstrukser.')
                )

                return HttpResponseRedirect('/')
            else:
                form = RegisterForm(request.POST, auto_id=True)
        else:
            form = RegisterForm()

        return render(request, 'auth/register.html', {'form': form, })


def verify(request, token):
    rt = get_object_or_404(RegisterToken, token=token)

    if rt.is_valid:
        email = get_object_or_404(Email, email=rt.email)
        email.verified = True
        email.save()

        user = getattr(rt, 'user')

        # If it is a stud email, set the ntnu_username for user
        if re.match(r'[^@]+@stud\.ntnu\.no', rt.email):
            user.ntnu_username = rt.email.split("@")[0]

            # Check if Online-member, and set Infomail to True is he/she is
            if user.is_member:
                user.infomail = True
                user.jobmail = True

        user_activated = False
        if not user.is_active:
            user.is_active = True
            user_activated = True

        user.save()
        rt.delete()

        if user_activated:
            messages.success(request, _(u'Bruker %s ble aktivert. Du kan nå logge inn.') % user.username)
            return redirect('auth_login')
        else:
            messages.success(request, _(u'Eposten %s er nå verifisert.') % email)
            return redirect('profile_add_email')

    else:
        messages.error(request, _(u'Denne lenken er utløpt. Bruk gjenopprett passord for å få tilsendt en ny lenke.'))
        return HttpResponseRedirect('/')


def recover(request):
    if request.user.is_authenticated():
        messages.error(request, _(u'Gjenoppretning av passord krever at du er logget ut.'))
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = RecoveryForm(request.POST)
            if form.is_valid():
                email_string = form.cleaned_data['email']
                emails = Email.objects.filter(email=email_string)

                if len(emails) == 0:
                    messages.error(request, _(u'Denne eposten er ikke registrert i våre systemer.'))
                    return HttpResponseRedirect('/')

                email = emails[0]

                # Create the registration token
                token = uuid.uuid4().hex
                rt = RegisterToken(user=email.user, email=email.email, token=token)
                rt.save()

                email_message = _(u"""
Vi har mottat forespørsel om å gjenopprette passordet for kontoen bundet til %s.
Dersom du ikke har bedt om denne handlingen ber vi deg se bort fra denne eposten.

Brukernavn: %s

Hvis du ønsker å gjennomføre en gjenoppretning av passord, bruk lenken under.

http://%s/auth/set_password/%s/

Denne lenken vil være gyldig i 24 timer. Dersom du behøver å få tilsendt en ny lenke
kan dette gjøres med funksjonen for å gjenopprette passord.
""") % (email.email, email.user.username, request.META['HTTP_HOST'], token)

                send_mail(_(u'Gjenoppretning av passord'), email_message, settings.DEFAULT_FROM_EMAIL, [email.email, ])

                messages.success(request, _(u'En lenke for gjenoppretning har blitt sendt til %s.') % email.email)

                return HttpResponseRedirect('/')
            else:
                form = RecoveryForm(request.POST, auto_id=True)
        else:
            form = RecoveryForm()

        return render(request, 'auth/recover.html', {'form': form})


@sensitive_post_parameters()
def set_password(request, token=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        tokens = RegisterToken.objects.filter(token=token)

        if tokens.count() == 1:
            rt = tokens[0]
            if rt.is_valid:
                if request.method == 'POST':
                    form = ChangePasswordForm(request.POST, auto_id=True)
                    if form.is_valid():
                        user = getattr(rt, 'user')

                        user.is_active = True
                        user.set_password(form.cleaned_data['new_password'])
                        user.save()

                        rt.delete()

                        messages.success(
                            request,
                            _(u'Bruker %s har gjennomført vellykket gjenoppretning av passord.' +
                              'Du kan nå logge inn.') % user.username
                        )

                        return HttpResponseRedirect('/')
                else:
                    form = ChangePasswordForm()

                    messages.success(request, _(u'Lenken er akseptert. Vennligst skriv inn ønsket passord.'))

                return render(request, 'auth/set_password.html', {'form': form, 'token': token})

        else:
            messages.error(
                request,
                _(u'Lenken er ugyldig. Vennligst bruk gjenoppretning av passord for å få tilsendt en ny lenke.')
            )
            return HttpResponseRedirect('/')


class UserViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    Viewset for User serializer. Supports filtering on 'username', 'first_name', 'last_name', 'email'
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    filter_fields = ('username', 'first_name', 'last_name', 'email')
