# -*- encoding: utf-8 -*-

from onlineweb.apps.offline.models import Offline
from onlineweb.apps.offline.models import Issue
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from onlineweb.decorators.view_decorators import html_view

@html_view('offline/offline.html')
def main(request):
	issues = Issue.objects.all()
	offline = Offline.objects.all()[0]
	return render_to_response("offline/offline.html", {"offline":offline, "issues":issues}, context_instance=RequestContext(request))

