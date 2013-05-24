#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

# Index page
def index(request):
	return render_to_response('resourcecenter/index.html', context_instance=RequestContext(request))
# Subpages
def notifier(request):
	return render_to_response('resourcecenter/notifier.html', context_instance=RequestContext(request))
def mailinglists(request):
	return render_to_response('resourcecenter/mailinglists.html', context_instance=RequestContext(request))
def infopages(request):
	return render_to_response('resourcecenter/infopages.html', context_instance=RequestContext(request))
def gameservers(request):
	return render_to_response('resourcecenter/gameservers.html', context_instance=RequestContext(request))
# def githubrepos(request):
# 	return render_to_response('resourcecenter/githubrepos.html', context_instance=RequestContext(request))
def irc(request):
	return render_to_response('resourcecenter/irc.html', context_instance=RequestContext(request))
