# -*- coding: utf-8 -*-
import json

from collections import namedtuple, defaultdict

from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from apps.feedback.models import (
    FeedbackRelation,
    FieldOfStudyAnswer,
    RATING_CHOICES,
    TextQuestion,
    TextAnswer,
    RegisterToken
)
from apps.feedback.forms import create_answer_forms


@login_required
def feedback(request, applabel, appmodel, object_id, feedback_id):
    fbr = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    if not fbr.can_answer(request.user):
        messages.error(request, fbr.answer_error_message(request.user))
        return redirect("home")

    if request.method == "POST":
        answers = create_answer_forms(fbr, post_data=request.POST)
        if all([a.is_valid() for a in answers]):
            for a in answers:
                a.save()

            # mark that the user has answered
            fbr.answered.add(request.user)
            fbr.save()

            # Set field of study automaticly
            fosa = FieldOfStudyAnswer(feedback_relation=fbr, answer=request.user.field_of_study)
            fosa.save()

            messages.success(request, _(u"Takk for at du svarte."))
            return redirect("home")
        else:
            messages.error(request, _(u"Du må svare på alle påkrevde felt."))
    else:
        answers = create_answer_forms(fbr)

    description = fbr.description

    return render(
        request,
        'feedback/answer.html',
        {'answers': answers, 'description': description}
    )


@staff_member_required
def result(request, applabel, appmodel, object_id, feedback_id):
    return feedback_results(request, applabel, appmodel, object_id, feedback_id)


def results_token(request, applabel, appmodel, object_id, feedback_id,  token):
    fbr = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)
    rt = get_object_or_404(RegisterToken, token=token)

    if rt.is_valid(fbr):
        return feedback_results(request, applabel, appmodel, object_id, feedback_id, True)
    else:
        return HttpResponse('Unauthorized', status=401)


def feedback_results(request, applabel, appmodel, object_id, feedback_id, token=False):
    fbr = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    qa = namedtuple("Qa", "question, answers")
    question_and_answers = []

    for question in fbr.questions:
        if (question.display or not token) and isinstance(question, TextQuestion):
            question_and_answers.append(qa(question, fbr.answers_to_question(question)))

    info = None

    if fbr.feedback.display_info or not token:
        info = fbr.content_info()
        info[_(u'Besvarelser')] = fbr.answered.count()

    rt = get_object_or_404(RegisterToken, fbr=fbr)

    token_url = u"%s%sresults/%s" % (request.META['HTTP_HOST'], fbr.get_absolute_url(), rt.token)

    return render(
        request,
        'feedback/results.html',
        {
            'question_and_answers': question_and_answers,
            'description': fbr.description,
            'token_url': token_url,
            'token': token,
            'info': info
        }
    )


@staff_member_required
def chart_data(request, applabel, appmodel, object_id, feedback_id):
    return get_chart_data(request, applabel, appmodel, object_id, feedback_id)


def chart_data_token(request, applabel, appmodel, object_id, feedback_id, token):
    fbr = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)
    rt = get_object_or_404(RegisterToken, token=token)

    if rt.is_valid(fbr):
        return get_chart_data(request, applabel, appmodel, object_id, feedback_id, True)
    else:
        return HttpResponse('Unauthorized', status=401)


def get_chart_data(request, applabel, appmodel, object_id, feedback_id, token=False):
    fbr = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    rating_answers = []
    rating_titles = []
    answer_collection = dict()
    answer_collection['replies'] = dict()
    answer_length = int(len(RATING_CHOICES))
    for question in fbr.ratingquestion:
        if question.display or not token:
            rating_titles.append(str(question))
            answers = fbr.answers_to_question(question)
            answer_count = [0] * answer_length
            for answer in answers:
                answer_count[int(answer.answer)] += 1
            rating_answers.append(answer_count[1:])

    fos_answer_count = defaultdict(int)

    if fbr.feedback.display_field_of_study or not token:
        fos = fbr.field_of_study_answers.all()
        for answer in fos:
            fos_answer_count[str(answer)] += 1

    mc_questions = []
    mc_answer_count = []

    for question in fbr.multiple_choice_question:
        if question.display or not token:
            mc_questions.append(unicode(question))
            answer_count = defaultdict(int)
            for answer in fbr.answers_to_question(question):
                answer_count[str(answer)] += 1
            mc_answer_count.append(answer_count.items())

    answer_collection['replies']['ratings'] = rating_answers
    answer_collection['replies']['titles'] = rating_titles
    answer_collection['replies']['mc_questions'] = mc_questions
    answer_collection['replies']['mc_answers'] = mc_answer_count
    answer_collection['replies']['fos'] = fos_answer_count.items()

    return HttpResponse(json.dumps(answer_collection), content_type='application/json')


@staff_member_required
def index(request):
    feedbacks = FeedbackRelation.objects.all()
    return render(request, 'feedback/index.html', {'feedbacks': feedbacks})


@staff_member_required
def delete_answer(request):
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        answer = get_object_or_404(TextAnswer, pk=answer_id)
        answer.delete()
        return HttpResponse(status=200)
    return HttpResponse(status=401)


def _get_fbr_or_404(app_label, app_model, object_id, feedback_id):
    """
    Get FeedbackRelation or raise Http404
    """
    try:
        ct = ContentType.objects.get(app_label=app_label, model=app_model)
        fbr = FeedbackRelation.objects.get(
            content_type=ct,
            object_id=object_id,
            feedback_id=feedback_id
        )
    except ObjectDoesNotExist:
        raise Http404

    return fbr
