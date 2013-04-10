#-*- coding: utf-8 -*-
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist
from apps.feedback.models import FeedbackRelation, FIELD_OF_STUDY_CHOICES
from apps.feedback.forms import create_answer_forms
from collections import namedtuple, defaultdict
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.utils.safestring import SafeString

def feedback(request, applabel, appmodel, object_id, feedback_id):
    fbr = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    if not fbr.can_answer(request.user):
        messages.error(request, _(u"Du kan ikke svare på dette skjemaet."))
        return redirect("home")

    if request.method == "POST":
        answers = create_answer_forms(fbr, post_data=request.POST)
        if all([a.is_valid() for a in answers]):
            for a in answers:
                a.save()

            # mark that the user has answered
            fbr.answered.add(request.user)
            fbr.save()

            messages.success(request, _("Takk for at du svarte"))
            return redirect("home")
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
    
    question = fbr.answers_to_question(fbr.fosquestion[0])
    answer_count = defaultdict(int)
    for answer in question:
        answer_count[str(answer)] += 1

    ordered_answers = []
    for _, x in FIELD_OF_STUDY_CHOICES[1:]:
        ordered_answers.append([x, answer_count[x]])
  
    description = fbr.description

    foschartdata = "["
    for a in ordered_answers:
        if a[1] > 0:
            foschartdata += simplejson.dumps({'label':a[0], 'value':a[1]}) + ','

    foschartdata = foschartdata[:-1] + ']'

    rating_questions = []
    for i in range(0, len(fbr.ratingquestion)):
        question = fbr.answers_to_question(fbr.ratingquestion[i])
        answers = [0] * 7
        for a in question:
            answers[int(a.answer)] += 1
        answers = answers[1:]
        rating_questions.append(answers)

    return render(request, 'feedback/results.html',
                  {'question_and_answers': question_and_answers, 'foschartdata': SafeString(foschartdata), 'description': description, "rating_questions": rating_questions})

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
