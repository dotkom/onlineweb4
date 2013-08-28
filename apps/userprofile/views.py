#-*- coding: utf-8 -*-
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from apps.userprofile.forms import create_profile_form, PrivacyForm, ProfileForm

import json


def index(request):

    '''
    This view is rendered for ever request made to the userprofile pages,
    due to the fact that it is a one-page view.
    '''

    if not request.user.is_authenticated():
        return render_home(request)

    dict = create_forms(request)

    # If a user has made a post, a session value will be set for which tab the user posted from.
    # This enables us to return the user to the correct tab when returning the view.
    # If no session key is set, return the user to the default first tab

    return render(request, 'userprofile/index.html', dict)


def render_home(request):
    messages.error(request, _(u"Du er ikke logget inn, og kan ikke se din profil."))
    return redirect('home')


def create_forms(request):
    dict = {
        'user_profile' : request.user.get_profile(),
        'privacy_form' : create_privacy_form(request),
        'user_profile_form' : create_user_profile_form(request),
    }

    if request.session.has_key('userprofile_active_tab'):
         dict['active_tab'] = request.session['userprofile_active_tab']
    else:
        dict['active_tab'] = 'myprofile'

    return dict


def create_user_profile_form(request):
    return create_profile_form(request.user.get_profile())


def create_privacy_form(request):
    return PrivacyForm(instance=request.user.privacy)


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

        userprofile = request.user.get_profile()
        dict = create_forms(request)
        user_profile_form = ProfileForm(request.POST)
        dict['user_profile_form'] = user_profile_form

        if not user_profile_form.is_valid():
            messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
            return render(request, 'userprofile/index.html', dict)

        userprofile.address = user_profile_form.cleaned_data['address']
        userprofile.allergies = user_profile_form.cleaned_data['allergies']
        userprofile.area_code = user_profile_form.cleaned_data['address']
        userprofile.infomail = user_profile_form.cleaned_data['infomail']
        userprofile.mark_rules = user_profile_form.cleaned_data['mark_rules']
        userprofile.nickname = user_profile_form.cleaned_data['nickname']
        userprofile.phone_number = user_profile_form.cleaned_data['phone_number']
        userprofile.website = user_profile_form.cleaned_data['website']
        request.user.email = user_profile_form.cleaned_data['email']

        userprofile.save()
        request.user.save()

    return redirect("userprofile")


def confirmDeleteImage(request):

    if request.is_ajax():
        if request.method == 'DELETE':
            userprofile = request.user.get_profile()
            userprofile.image = None
            userprofile.save()

            return HttpResponse(status=204)
    return HttpResponse(status=405)


def savePrivacy(request):

    if not request.user.is_authenticated():
        return render_home(request)

    if request.method == 'POST':
        dict = create_forms(request)
        privacy_form = PrivacyForm(request.POST, instance=request.user.privacy)
        dict['privacy_form'] = privacy_form

        if not privacy_form.is_valid():
            messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
            return render(request, 'userprofile/index.html', dict)

        privacy_form.save()

    return redirect("userprofile")