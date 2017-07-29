# -*- coding: utf-8 -*-

from django.shortcuts import render


# Index page
def index(request):
    return render(request, 'resourcecenter/index.html')
