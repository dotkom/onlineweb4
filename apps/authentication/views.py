# -*- coding: utf-8 -*-
import logging
import re
import uuid
from smtplib import SMTPException

from django.conf import settings
from django.contrib import auth, messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
# API v1
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.authentication.forms import ChangePasswordForm, LoginForm, RecoveryForm, RegisterForm
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Email, RegisterToken
from apps.authentication.serializers import UserSerializer


@sensitive_post_parameters()
def login(request):
    redirect_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.login(request):
            messages.success(request, _('Du er nå logget inn.'), extra_tags='data-dismiss')
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
    messages.success(request, _('Du er nå logget ut.'), extra_tags='data-dismiss')
    return HttpResponseRedirect('/')


@sensitive_post_parameters()
def register(request):
    log = logging.getLogger(__name__)

    if request.user.is_authenticated():
        messages.error(request, _('Registrering av ny konto krever at du er logget ut.'))
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

                try:
                    rt = RegisterToken(user=user, email=email.email, token=token)
                    rt.save()
                    log.info('Successfully registered token for %s' % request.user)
                except IntegrityError as ie:
                    log.error('Failed to register token for "%s" due to "%s"' % (request.user, ie))

                email_context = {}
                verify_url = reverse('auth_verify', args=(token,))
                email_context['verify_url'] = request.build_absolute_uri(verify_url)

                message = render_to_string('auth/email/welcome_tpl.txt', email_context)

                try:
                    send_mail(_('Verifiser din konto'), message, settings.DEFAULT_FROM_EMAIL, [email.email, ])
                except SMTPException:
                    messages.error(request, 'Det oppstod en kritisk feil, epostadressen er ugyldig!')
                    return redirect('home')

                messages.success(
                    request,
                    _('Registreringen var vellykket. Se tilsendt epost for verifiseringsinstrukser.')
                )

                return HttpResponseRedirect('/')
            else:
                form = RegisterForm(request.POST, auto_id=True)
        else:
            form = RegisterForm()

        return render(request, 'auth/register.html', {'form': form, })


def verify(request, token):
    log = logging.getLogger(__name__)
    rt = get_object_or_404(RegisterToken, token=token)

    if rt.is_valid:
        email = get_object_or_404(Email, email=rt.email)
        email.verified = True
        email.save()

        user = getattr(rt, 'user')

        # If it is a stud email, set the ntnu_username for user
        if re.match(r'[^@]+@stud\.ntnu\.no', rt.email):
            user.ntnu_username = rt.email.split("@")[0]
            log.info('Set ntnu_username for user %s to %s' % (user, rt.email))

            # Check if Online-member, and set Infomail to True is he/she is
            if user.is_member:
                user.infomail = True

        user_activated = False
        if not user.is_active:
            user.is_active = True
            user_activated = True

        user.save()
        rt.delete()

        if user_activated:
            log.info('New user %s was activated' % user)
            user.backend = "django.contrib.auth.backends.ModelBackend"
            auth.login(request, user)
            messages.success(request, _(
                'Bruker %s ble aktivert. Du er nå logget inn. '
                'Kikk rundt på "Min Side" for å oppdatere profilinnstillinger.') % user.username)
            return redirect('profiles')
        else:
            log.info('New email %s was verified for user %s' % (email, user))
            messages.success(request, _('Eposten %s er nå verifisert.') % email)
            return redirect('profile_add_email')

    else:
        log.debug('Failed to verify email due to invalid register token')
        messages.error(request, _('Denne lenken er utløpt. Bruk gjenopprett passord for å få tilsendt en ny lenke.'))
        return HttpResponseRedirect('/')


def recover(request):
    log = logging.getLogger(__name__)
    if request.user.is_authenticated():
        messages.error(request, _('Gjenoppretning av passord krever at du er logget ut.'))
        return HttpResponseRedirect('/')
    else:
        if request.method == 'POST':
            form = RecoveryForm(request.POST)
            if form.is_valid():
                email_string = form.cleaned_data['email']
                emails = Email.objects.filter(email=email_string)

                if len(emails) == 0:
                    messages.error(request, _('Denne eposten er ikke registrert i våre systemer.'))
                    return HttpResponseRedirect('/')

                email = emails[0]

                # Create the registration token
                token = uuid.uuid4().hex
                try:
                    rt = RegisterToken(user=email.user, email=email.email, token=token)
                    rt.save()
                    log.info('Successfully registered token for %s' % request.user)
                except IntegrityError as ie:
                    log.error('Failed to register token for "%s" due to "%s"' % (request.user, ie))
                    raise ie

                email_context = {}
                email_context['email'] = email.email
                email_context['username'] = email.user.username
                set_password_url = reverse('auth_set_password', args=(token,))
                email_context['reset_url'] = request.build_absolute_uri(set_password_url)

                email_message = render_to_string('auth/email/password_reset_tpl.txt', email_context)

                send_mail(_('Gjenoppretting av passord'), email_message, settings.DEFAULT_FROM_EMAIL, [email.email, ])

                messages.success(request, _('En lenke for gjenoppretting har blitt sendt til %s.') % email.email)

                return HttpResponseRedirect('/')
            else:
                form = RecoveryForm(request.POST, auto_id=True)
        else:
            form = RecoveryForm()

        return render(request, 'auth/recover.html', {'form': form})


@sensitive_post_parameters()
def set_password(request, token=None):
    log = logging.getLogger(__name__)
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        rt = None
        try:
            rt = RegisterToken.objects.get(token=token)
        except RegisterToken.DoesNotExist:
            log.debug('%s tried to set password with nonexisting/expired token %s' % (request.user, token))
            messages.error(request, 'Denne lenken er utløpt. Bruk gjenopprett passord for å få tilsendt en ny lenke.')
        if rt and rt.is_valid:
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
                        _('Passordgjenoppretting gjennomført for "%s". ' +
                          'Du kan nå logge inn.') % user.username
                    )
                    log.info('User "%s" successfully recovered password.' % request.user)
                    return HttpResponseRedirect('/')
                else:
                    messages.error(request, 'Noe gikk galt med gjenoppretting av passord. Vennligst prøv igjen.')
                    log.debug('User %s failed to recover password with token %s. '
                              '[form.is_valid => False]' % (request.user, rt))
                    return HttpResponseRedirect('/')
            else:
                form = ChangePasswordForm()
                messages.success(request, _('Lenken er akseptert. Vennligst skriv inn ønsket passord.'))
            return render(request, 'auth/set_password.html', {'form': form, 'token': token})
        log.debug('User %s failed to recover password with token %s.' % (request.user, rt))
        messages.error(
            request, 'Noe gikk galt med gjenoppretning av passord. Vennligst prøv igjen.')
        return HttpResponseRedirect('/')


class UserViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    Viewset for User serializer. Supports filtering on 'username', 'first_name', 'last_name', 'email'
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    filter_fields = ('username', 'first_name', 'last_name', 'rfid',)
