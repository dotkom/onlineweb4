#-*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import redirect

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from apps.profiles.forms import PrivacyForm, ProfileForm

import json

"""
    Index for the entire user profile view
    Methods redirect to this view on save
"""
def index(request):

    """
    This view is rendered for ever request made to the userprofile pages,
    due to the fact that it is a one-page view.
    """

    if not request.user.is_authenticated():
        return render_home(request)

    dict = create_request_dictionary(request)

    # If a user has made a post, a session value will be set for which tab the user posted from.
    # This enables us to return the user to the correct tab when returning the view.
    # If no session key is set, return the user to the default first tab

    return render(request, 'profiles/index.html', dict)


def render_home(request):
    messages.error(request, _(u"Du er ikke logget inn, og kan ikke se din profil."))
    return redirect('home')


def create_request_dictionary(request):
    dict = {
        'privacy_form' : PrivacyForm(instance=request.user.privacy),
        'user_profile_form' : ProfileForm(instance=request.user),
        'password_change_form' : PasswordChangeForm(request.user)

    }

    if request.session.has_key('userprofile_active_tab'):
         dict['active_tab'] = request.session['userprofile_active_tab']
    else:
        dict['active_tab'] = 'myprofile'

    return dict


def updateActiveTab(request):

    if request.is_ajax():
        if request.method == 'POST':
            value = json.loads(request.body)
            request.session['userprofile_active_tab'] = value['active_tab']

            return HttpResponse(status=200)
    return HttpResponse(status=405)

def saveUserProfile(request):

    if not request.user.is_authenticated():
        return render_home(request)

    if request.method == 'POST':

        user = request.user
        dict = create_request_dictionary(request)
        user_profile_form = ProfileForm(request.POST)
        dict['user_profile_form'] = user_profile_form

        if not user_profile_form.is_valid():
            messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
            return render(request, 'profiles/index.html', dict)

        user.address = user_profile_form.cleaned_data['address']
        user.allergies = user_profile_form.cleaned_data['allergies']
        user.area_code = user_profile_form.cleaned_data['address']
        user.infomail = user_profile_form.cleaned_data['infomail']
        user.mark_rules = user_profile_form.cleaned_data['mark_rules']
        user.nickname = user_profile_form.cleaned_data['nickname']
        user.phone_number = user_profile_form.cleaned_data['phone_number']
        user.website = user_profile_form.cleaned_data['website']
        user.email = user_profile_form.cleaned_data['email']

        user.save()
        messages.success(request, _(u"Brukerprofilen din ble endret"))

    return redirect("profiles")


def confirmDeleteImage(request):

    if request.is_ajax():
        if request.method == 'DELETE':
            request.user.image = None
            request.user.save()

            return HttpResponse(status=204)
    return HttpResponse(status=405)


def savePrivacy(request):

    if not request.user.is_authenticated():
        return render_home(request)

    if request.method == 'POST':
        dict = create_request_dictionary(request)
        privacy_form = PrivacyForm(request.POST, instance=request.user.privacy)
        dict['privacy_form'] = privacy_form

        if not privacy_form.is_valid():
            messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
            return render(request, 'profiles/index.html', dict)

        privacy_form.save()
        messages.success(request, _(u"Personvern ble endret"))

    return redirect("profiles")


def savePassword(request):

    if not request.user.is_authenticated():
        return render_home(request)

    if request.method == 'POST':
        dict = create_request_dictionary(request)
        password_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        dict['password_change_form'] = password_change_form

        if not password_change_form.is_valid():
            messages.error(request, _(u"Passordet ditt ble ikke endret"))
            return render(request, 'profiles/index.html', dict)

        password_change_form.save()
        messages.success(request, _(u"Passordet ditt ble endret"))

    return redirect("profiles")