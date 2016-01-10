# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext


# Index page
def index(request):
    return render_to_response('resourcecenter/index.html', context_instance=RequestContext(request))


# Subpages
def gameservers(request):
    return render_to_response('resourcecenter/gameservers.html', context_instance=RequestContext(request))
