# -*- coding: utf-8 -*-

from django.shortcuts import render
from apps.resourcecenter.models import Resource


# Index page
def index(request):
    resources = Resource.objects.all().order_by('-priority')
    context = {
        'resources': resources,
    }
    return render(request, 'resourcecenter/index.html', context)
