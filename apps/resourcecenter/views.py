#-*- coding: utf-8 -*-
# from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
# from apps.resourcecenter.models import Event, AttendanceEvent, Attendee
# import datetime


def index(request):
	# return HttpResponse('HEI! :D:D:D::D:D:D:D')
	return render_to_response('resourcecenter/index.html', context_instance=RequestContext(request))
