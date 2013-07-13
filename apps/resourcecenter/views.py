#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

# Index page
def index(request):
	return render_to_response('resourcecenter/index.html', context_instance=RequestContext(request))
# Subpages
def mailinglists(request):
    return render_to_response('resourcecenter/mailinglists.html', context_instance=RequestContext(request))
def gameservers(request):
	return render_to_response('resourcecenter/gameservers.html', context_instance=RequestContext(request))
