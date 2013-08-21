#-*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from apps.userprofile.models import UserProfile, Privacy
from apps.userprofile.forms import ProfileForm, createFromUserProfile


def index(request):

    if not request.user.is_authenticated():
        return renderHome(request)

    userinfo = getUserInfo(request)
    user = userinfo['user']
    userprofile = userinfo['userprofile']

    form = createFromUserProfile(userprofile)

    dict = {
        'userprofile' : userprofile,
        'form' : form
    }

    return render(request, 'userprofile/index.html', dict)


def renderHome(request):
    messages.error(request, _(u"Du er ikke logget inn, og kan ikke se din profil."))
    return redirect('home')

def getUserInfo(request):
    user = User.objects.get(id = request.user.id)
    return {
        'user' : user,
        'userprofile' : user.userprofile.filter(user = user)[0]
    }

def saveUserProfile(request):

    if not request.user.is_authenticated():
        return renderHome(request)

    userinfo = getUserInfo(request)
    user = userinfo['user']
    userprofile = userinfo['userprofile']

    form = ProfileForm(request.POST)
    dict = {
            'userprofile' : userprofile,
            'form' : form
    }

    if not form.is_valid():
        messages.error(request, _(u"Noen av de påkrevde feltene mangler"))
        return render(request, 'userprofile/index.html', dict)

    if request.method == 'POST':
        userprofile.address = form.cleaned_data['address']
        userprofile.allergies = form.cleaned_data['allergies']
        userprofile.area_code = form.cleaned_data['address']
        userprofile.infomail = form.cleaned_data['infomail']
        userprofile.mark_rules = form.cleaned_data['mark_rules']
        userprofile.nickname = form.cleaned_data['nickname']
        userprofile.phone_number = form.cleaned_data['phone_number']
        userprofile.website = form.cleaned_data['website']
        user.email = form.cleaned_data['email']

        userprofile.save()
        user.save()

    return redirect("userprofile")


def confirmDeleteImage(request):

    if request.is_ajax():
        if request.method == 'DELETE':
            user = User.objects.get(id = request.user.id)
            userprofile = user.userprofile.filter(user = user)[0]

            userprofile.image = None
            userprofile.save()

            return HttpResponse(status=204)
    return HttpResponse(status=405)