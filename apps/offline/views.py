# -*- encoding: utf-8 -*-

from onlineweb.apps.offline.models import Offline
from onlineweb.apps.offline.models import Issue
from django.shortcuts import render
from django.template.context import RequestContext

from onlineweb.decorators.view_decorators import html_view

def main(request):
	issues = Issue.objects.all()
	offline = Offline.objects.all()[0]
	return render("offline/offline.html", {"offline":offline, "issues":issues})

