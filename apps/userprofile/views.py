#-*- coding: utf-8 -*-
from django.shortcuts import render

def index(request):

    #user = request.user

    #userprofile = request.user.userprofile
    #privacy = request.user.privacy

    dict = {
        #'userprofile' : userprofile,
        #'privacy' : privacy
    }

    return render(request, 'userprofile/index.html', dict)



