#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from apps.feedback.models import Feedback
from apps.feedback.models import Question
from apps.feedback.models import FieldOfStudyQuestion
from apps.feedback.models import TextQuestion
from apps.feedback.models import Answer
from apps.feedback.models import TextAnswer
from apps.feedback.models import FieldOfStudyAnswer


def index(request):
    feedbacks = Feedback.objects.all()
    return render_to_response('feedback/index.html', {'feedbacks': feedbacks}, context_instance=RequestContext(request))

