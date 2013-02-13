# -*- encoding: utf-8 -*-

from apps.offline.models import Offline
from django.shortcuts import render
from django.template.context import RequestContext

def main(request):
	issues = Offline.issues()
	return render(request, "offline/offline.html", { "issues":issues })

