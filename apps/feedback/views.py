#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.feedback.models import Feedback


def index(request):
    feedbacks = Feedback.objects.all()
    return render_to_response('feedback/index.html', {'feedbacks': feedbacks}, context_instance=RequestContext(request))
