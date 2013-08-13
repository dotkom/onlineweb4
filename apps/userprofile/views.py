#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.shortcuts import render
from apps.userprofile.models import UserProfile, Privacy
from apps.userprofile.forms import ProfileForm

def index(request):

    user = User.objects.get(id = request.user.id)
    userprofile = user.userprofile.filter(user = user)[0]

    form = ProfileForm(initial = {
        'infomail' : userprofile.infomail,
        'address' : userprofile.address,
        'area_code' : userprofile.area_code,
        'allergies' : userprofile.allergies,
        'mark_rules' : userprofile.mark_rules,
        'image' : userprofile.image,
        'nickname' : userprofile.nickname,
        'website' : userprofile.website,
        'email' : userprofile.user.email,
        'phone_number' : userprofile.phone_number
    })

    dict = {
        'userprofile' : userprofile,
        'form' : form
    }

    return render(request, 'userprofile/index.html', dict)



