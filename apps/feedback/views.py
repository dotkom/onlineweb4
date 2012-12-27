#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from apps.feedback.models import Feedback
from apps.feedback.models import FeedbackRelation


def feedback(request, applabel, appmodel, object_id, feedback_id):
    try:
        ct = ContentType.objects.get(app_label=applabel, model=appmodel)
        fbr = FeedbackRelation.objects.get(content_type=ct,
                                           object_id=object_id,
                                           feedback_id=feedback_id)
    except ObjectDoesNotExist:
        return HttpResponse("fant ikke skjemaet")

    return HttpResponse(fbr.feedback.description)


def index(request):
    feedbacks = Feedback.objects.all()
    return render_to_response('feedback/index.html', {'feedbacks': feedbacks}, context_instance=RequestContext(request))
