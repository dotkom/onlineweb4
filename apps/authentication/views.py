# -*- coding: utf-8 -*-

import uuid

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from apps.authentication.forms import (LoginForm, RegisterForm, 
                            RecoveryForm, ChangePasswordForm)
from apps.authentication.models import RegisterToken
from apps.userprofile.models import UserProfile

def login(request):
    redirect_url = request.REQUEST.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.login(request):
            messages.success(request, _(u'Du er nå logget inn.'))
            if redirect_url:
                return HttpResponseRedirect(redirect_url)
            return HttpResponseRedirect('/')
        else: form = LoginForm(request.POST, auto_id=True)
    else:
        form = LoginForm()

    response_dict = { 'form' : form, 'next' : redirect_url}
    return render(request, 'auth/login.html', response_dict)

def logout(request):
    auth.logout(request)
    messages.success(request, _(u'Du er nå logget ut.'))
    return HttpResponseRedirect('/')

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
                    first_name=cleaned['first_name'], 
                    last_name=cleaned['last_name'],
                    email=cleaned['email'],
                )
                user.set_password(cleaned['password'])
                user.is_active = False
                user.save()

                print user

                # Fill in userprofile, it was automatically made when user was saved.
                # See bottom of apps/userprofile/models.py
                up = user.get_profile()
                #date_of_birth=cleaned['date_of_birth'],
                up.area_code=cleaned['zip_code'],
                up.address=cleaned['address'],
                up.phone_number=cleaned['phone'],
                up.save() 

                # Create the registration token
                token = uuid.uuid4().hex
                rt = RegisterToken(user=user, token=token)
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

                send_mail(_(u'Verifiser din konto'), email_message, settings.DEFAULT_FROM_EMAIL, [user.email,])

                messages.success(request, _(u'Registreringen var vellykket. Se tilsendt epost for verifiseringsinstrukser.'))

                return HttpResponseRedirect('/')        
            else:
                form = RegisterForm(request.POST, auto_id=True)
        else:
            form = RegisterForm()

        return render(request, 'auth/register.html', {'form': form, })

def verify(request, token):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        rt = get_object_or_404(RegisterToken, token=token)
        
        if rt.is_valid:
            user = getattr(rt, 'user')

            user.is_active = True
            user.save()
            rt.delete()

            messages.success(request, _(u'Bruker %s ble aktivert. Du kan nå logge inn.') % user.username)
            return redirect('auth_login')
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
                email = form.cleaned_data['email']
                users = User.objects.filter(email=email)

                if len(users) == 0:
                    messages.error(request, _(u'Denne eposten er ikke registrert i våre systemer.'))
                    return HttpResponseRedirect('/')        

                user = users[0]
                user.save()
    
                # Create the registration token
                token = uuid.uuid4().hex
                rt = RegisterToken(user=user, token=token)
                rt.save()

                email_message = _(u"""
Vi har mottat forespørsel om å gjenopprette passordet for kontoen bundet til %s.
Dersom du ikke har bedt om denne handlingen ber vi deg se bort fra denne eposten.

Brukernavn: %s

Hvis du ønsker å gjennomføre en gjenoppretning av passord, bruk lenken under.

http://%s/auth/set_password/%s/

Denne lenken vil være gyldig i 24 timer. Dersom du behøver å få tilsendt en ny lenke
kan dette gjøres med funksjonen for å gjenopprette passord.
""") % (email, user.username, request.META['HTTP_HOST'], token)

                send_mail(_(u'Gjenoppretning av passord'), email_message, settings.DEFAULT_FROM_EMAIL, [email,])

                messages.success(request, _(u'En lenke for gjenoppretning har blitt sendt til %s.') % email)

                return HttpResponseRedirect('/')        
            else:
                form = RecoveryForm(request.POST, auto_id=True)
        else:
            form = RecoveryForm()

        return render(request, 'auth/recover.html', {'form': form})

def set_password(request, token=None): 
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        rt = get_object_or_404(RegisterToken, token=token)
       
        if rt.is_valid:
            if request.method == 'POST':
                form = ChangePasswordForm(request.POST, auto_id=True)
                if form.is_valid():
                    user = getattr(rt, 'user')

                    user.is_active = True
                    user.set_password(form.cleaned_data['new_password'])
                    user.save()
                    
                    rt.delete()

                    messages.success(request, _(u'Bruker %s har gjennomført vellykket gjenoppretning av passord. Du kan nå logge inn.') % user)
                    
                    return HttpResponseRedirect('/')        
            else:
                
                form = ChangePasswordForm()

                messages.success(request, _(u'Lenken er akseptert. Vennligst skriv inn ønsket passord.'))

            return render(request, 'auth/set_password.html', {'form': form, 'token': token})

        else:
            messages.error(request, _(u'Lenken er utløpt. Vennligst bruk gjenoppretning av passord for å få tilsendt en ny lenke.'))
            return HttpResponseRedirect('/')        
