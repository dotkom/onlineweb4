#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from apps.feedback.models import FeedbackRelation
from apps.feedback.forms import create_answer_forms
from collections import namedtuple


def feedback(request, applabel, appmodel, object_id, feedback_id):
    fbr = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    if not fbr.can_answer(request.user):
        return HttpResponse("Du kan ikke svare på dette skjemaet nå.")

    if request.method == "POST":
        answers = create_answer_forms(fbr, post_data=request.POST)
        if all([a.is_valid() for a in answers]):
            for a in answers:
                a.save()

            # mark that the user has answered
            fbr.answered.add(request.user)
            fbr.save()
            return HttpResponse("Du svarte!")
    else:
        answers = create_answer_forms(fbr)

    return render(request, 'feedback/answer.html',
                  {'answers': answers})


def result(request, applabel, appmodel, object_id, feedback_id):
    fbr = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    Qa = namedtuple("Qa", "question, answers")
    question_and_answers = []
    for q in fbr.questions:
        question_and_answers.append(Qa(q, fbr.answers_to_question(q)))

    return render(request, 'feedback/results.html',
                  {'question_and_answers': question_and_answers})


def index(request):
    feedbacks = FeedbackRelation.objects.all()
    return render_to_response('feedback/index.html',
                              {'feedbacks': feedbacks},
                              context_instance=RequestContext(request))


def _get_fbr_or_404(app_label, app_model, object_id, feedback_id):
    """
    Get FeedbackRelation or raise Http404
    """
    try:
        ct = ContentType.objects.get(app_label=app_label, model=app_model)
        fbr = FeedbackRelation.objects.get(content_type=ct,
                                           object_id=object_id,
                                           feedback_id=feedback_id)
    except ObjectDoesNotExist:
        raise Http404

    return fbr
