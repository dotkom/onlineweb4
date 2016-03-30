# -*- coding: utf-8 -*-
import json
from collections import defaultdict, namedtuple

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

from apps.feedback.forms import create_forms
from apps.feedback.models import (RATING_CHOICES, FeedbackRelation, FieldOfStudyAnswer,
                                  RegisterToken, TextAnswer, TextQuestion)
from apps.feedback.utils import can_delete, get_group_restricted_feedback_relations, has_permission


@login_required
def feedback(request, applabel, appmodel, object_id, feedback_id):
    feedback_relation = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    if not feedback_relation.can_answer(request.user):
        messages.error(request, feedback_relation.answer_error_message(request.user))
        return redirect("home")

    if request.method == "POST":
        questions = create_forms(feedback_relation, post_data=request.POST)
        if all([answer.is_valid() for answer in questions]):
            for answer in questions:
                answer.save()

            # mark that the user has answered
            feedback_relation.answered.add(request.user)
            feedback_relation.save()

            # Set field of study automaticly
            fosa = FieldOfStudyAnswer(feedback_relation=feedback_relation, answer=request.user.field_of_study)
            fosa.save()

            messages.success(request, _("Takk for at du svarte."))
            return redirect("home")
        else:
            messages.error(request, _("Du må svare på alle påkrevde felt."))
    else:
        questions = create_forms(feedback_relation)

    description = feedback_relation.description

    return render(
        request,
        'feedback/answer.html',
        {'questions': questions, 'description': description}
    )


@login_required
def result(request, applabel, appmodel, object_id, feedback_id):
    feedback_relation = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    if not has_permission(feedback_relation, request.user):
        messages.error(request, _("Du har ikke tilgang til dette skjemaet."))
        return redirect("home")

    return feedback_results(request, feedback_relation)


def results_token(request, applabel, appmodel, object_id, feedback_id,  token):
    feedback_relation = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)
    register_token = get_object_or_404(RegisterToken, token=token)

    if register_token.is_valid(feedback_relation):
        return feedback_results(request, feedback_relation, True)
    else:
        return HttpResponse('Unauthorized', status=401)


def feedback_results(request, feedback_relation, token=False):
    qa = namedtuple("Qa", "question, answers")
    question_and_answers = []

    for question in feedback_relation.questions:
        if (question.display or not token) and isinstance(question, TextQuestion):
            question_and_answers.append(qa(question, feedback_relation.answers_to_question(question)))

    info = None

    if feedback_relation.feedback.display_info or not token:
        info = feedback_relation.content_info()
        info[_('Besvarelser')] = feedback_relation.answered.count()

    register_token = get_object_or_404(RegisterToken, fbr=feedback_relation)

    token_url = "%s%sresults/%s" % (
        request.META['HTTP_HOST'],
        feedback_relation.get_absolute_url(),
        register_token.token
    )

    return render(
        request,
        'feedback/results.html',
        {
            'question_and_answers': question_and_answers,
            'description': feedback_relation.description,
            'token_url': token_url,
            'token': token,
            'info': info
        }
    )


@login_required
def chart_data(request, applabel, appmodel, object_id, feedback_id):
    feedback_relation = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)

    if not has_permission(feedback_relation, request.user):
        messages.error(request, _("Du har ikke tilgang til denne dataen."))
        return redirect("home")

    return get_chart_data(request, feedback_relation)


def chart_data_token(request, applabel, appmodel, object_id, feedback_id, token):
    feedback_relation = _get_fbr_or_404(applabel, appmodel, object_id, feedback_id)
    register_token = get_object_or_404(RegisterToken, token=token)

    if register_token.is_valid(feedback_relation):
        return get_chart_data(request, feedback_relation, True)
    else:
        return HttpResponse('Unauthorized', status=401)


def get_chart_data(request, feedback_relation, token=False):
    rating_answers = []
    rating_titles = []
    answer_collection = dict()
    answer_collection['replies'] = dict()
    answer_length = int(len(RATING_CHOICES))
    for question in feedback_relation.ratingquestion:
        if question.display or not token:
            rating_titles.append(str(question))
            answers = feedback_relation.answers_to_question(question)
            answer_count = [0] * answer_length
            for answer in answers:
                answer_count[int(answer.answer)] += 1
            rating_answers.append(answer_count[1:])

    fos_answer_count = defaultdict(int)

    if feedback_relation.feedback.display_field_of_study or not token:
        fos = feedback_relation.field_of_study_answers.all()
        for answer in fos:
            fos_answer_count[str(answer)] += 1

    mc_questions = []
    mc_answer_count = []

    for question in feedback_relation.multiple_choice_question:
        if question.display or not token:
            mc_questions.append(str(question))
            answer_count = defaultdict(int)
            for answer in feedback_relation.answers_to_question(question):
                answer_count[str(answer)] += 1
            mc_answer_count.append(list(answer_count.items()))

    answer_collection['replies']['ratings'] = rating_answers
    answer_collection['replies']['titles'] = rating_titles
    answer_collection['replies']['mc_questions'] = mc_questions
    answer_collection['replies']['mc_answers'] = mc_answer_count
    answer_collection['replies']['fos'] = list(fos_answer_count.items())

    return HttpResponse(json.dumps(answer_collection), content_type='application/json')


@login_required
def index(request):
    feedback_relations = get_group_restricted_feedback_relations(request.user)
    return render(request, 'feedback/index.html', {'feedbacks': feedback_relations})


@login_required
def delete_answer(request):
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        answer = get_object_or_404(TextAnswer, pk=answer_id)

        if can_delete(answer, request.user):
            answer.delete()
            return HttpResponse(status=200)

    return HttpResponse(_("Du har ikke tilgang til å slette dette svaret", status=401))


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
