# -*- coding: utf-8 -*-

import json
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

from apps.genfors.forms import (AlternativeFormSet, LoginForm, MeetingForm, QuestionForm,
                                RegisterVoterForm)
from apps.genfors.models import (BOOLEAN_VOTE, MULTIPLE_CHOICE, Alternative, BooleanVote, Meeting,
                                 MultipleChoice, Question, RegisteredVoter, Result)
from apps.genfors.utils import (anonymous_voter, generate_genfors_context, get_active_meeting,
                                get_next_meeting, handle_login, is_admin)


@login_required
def genfors(request):
    context = {}
    meeting = get_active_meeting()

    # Check for active meeting
    if not meeting:
        return render(request, "genfors/index.html", context)

    reg_voter = RegisteredVoter.objects.filter(user=request.user, meeting=meeting).first()
    try:
        anon_voter = anonymous_voter(request.COOKIES['anon_voter'], request.user.username)
    except KeyError:
        anon_voter = None
    # Check for cookie voter hash
    if anon_voter:
        context['meeting'] = meeting
        context['registered_voter'] = reg_voter

        # If there is an active question
        aq = meeting.get_active_question()

        context = generate_genfors_context(aq, context, anon_voter, reg_voter)

        return render(request, "genfors/index.html", context)

    # If user is not logged in
    else:
        # Process stuff from the login form
        if request.method == 'POST':
            form = RegisterVoterForm(request.POST)
            context['form'] = form
            response = []
            if form.is_valid():
                response = handle_login(request, context)

            elif 'anon_voter' in request.COOKIES:
                response = render(request, "genfors/index_login.html", context)
                # Delete old hash
                response.delete_cookie('anon_voter')
            return response

        # Set registration_locked context and create login form
        else:
            context['form'] = RegisterVoterForm()
            if not reg_voter:
                context['registration_locked'] = meeting.registration_locked

    aq = meeting.get_active_question()
    context = generate_genfors_context(aq, context, anon_voter, reg_voter)
    return render(request, "genfors/index_login.html", context)


@login_required
def registered_voters(request):
    context = {}
    if is_admin(request):
        meeting = get_active_meeting()
        if meeting:
            context['registered_voters'] = meeting.get_attendee_list()
        return render(request, "genfors/registered_voters.html", context)
    else:
        messages.error(request, 'Du har ikke tilgang til dette')
        return redirect('genfors_admin')


@login_required
def admin(request):
    context = {}
    # Check if user is logged in as genfors admin
    if is_admin(request):
        meeting = get_next_meeting()
        if meeting:
            aq = meeting.get_active_question()
            a = anonymous_voter(request.COOKIES.get('anon_voter'), request.user.username)
            r = RegisteredVoter.objects.filter(user=request.user, meeting=meeting).first()
            if aq:
                context['not_voted'] = None
                v = a if aq.anonymous else r
                context['already_voted'] = aq.already_voted(v)
                not_voted = []
                for person in meeting.get_can_vote():
                    if not aq.already_voted(person):
                        not_voted.append(person)
                context['not_voted'] = not_voted

            context['meeting'] = meeting
            context['question'] = aq
            context['questions'] = meeting.get_locked_questions()
            context['pin_code'] = meeting.get_pin_code()
        elif request.method == 'POST':
            form = MeetingForm(request.POST)
            context['form'] = form
            if form.is_valid():
                meeting = Meeting(title=form.cleaned_data['title'],
                                  start_date=form.cleaned_data['start_date'])
                meeting.save()
                meeting.generate_pin_code()
                messages.success(request, _('Generalforsamling lagt til'))
                return redirect('genfors_admin')
        else:
            # Create meeting view
            form = MeetingForm()
            context['form'] = form
        context['meetings'] = Meeting.objects.filter(ended=True).order_by('-start_date', '-id')
        return render(request, "genfors/admin.html", context)
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            context['form'] = form
            if form.is_valid():
                request.session['genfors_admin'] = True
                return redirect('genfors_admin')
        else:
            context['form'] = LoginForm()
    return render(request, "genfors/admin_login.html", context)


def admin_logout(request):
    if is_admin(request):
        del request.session['genfors_admin']
    return redirect('genfors_index')


@login_required
def question_admin(request, question_id=None):
    context = {}
    meeting = get_active_meeting()
    if is_admin(request):
        if not meeting:
            return _handle_inactive_meeting(request)

        if question_id is None and meeting.get_active_question():
            messages.error(request, _('Kan ikke legge til et nytt spørsmål når det allerede er et aktivt et'))
            return redirect('genfors_admin')

        if request.method == 'POST':
            return handle_question_admin_update(request, context, question_id)
        else:
            return handle_question_admin_detail(request, context, question_id)

    else:
        messages.error(request, 'Du har ikke tilgang til dette')
    return redirect('genfors_admin')


@require_http_methods(["POST"])
@login_required
def user_can_vote(request):
    if is_admin(request):
        json_response = {'success': False}
        m = get_active_meeting()
        if m:
            user_id = request.POST.get('user-id')
            try:
                user_id = int(user_id)
                user = RegisteredVoter.objects.get(meeting=m, id=user_id)
                # Changing can_vote
                user.can_vote = not user.can_vote
                user.save()
                json_response['can_vote'] = user.can_vote
                json_response['success'] = True
            except ValueError:
                json_response['error'] = 'Brukerid ikke gyldig'
            except RegisteredVoter.DoesNotExist:
                json_response['error'] = 'Bruker ikke funnet'
        else:
            json_response['error'] = 'Det er ingen aktiv generalforsamling'
        return HttpResponse(json.dumps(json_response))
    return HttpResponse(status_code=403, reason_phrase='Forbidden')


@login_required
def question_close(request, question_id):
    response = question_validate(request, question_id)
    if response:
        return response

    q = Question.objects.get(id=question_id)
    m = get_active_meeting()
    if request.method == 'POST':
        q.total_voters = m.num_can_vote()
        result = Result(
            meeting=m, question=q, result_private=json.dumps(q.get_admin_results()),
            result_public=json.dumps(q.get_results())
        )
        result.save()
        q.locked = True
        q.save()
        messages.success(request, 'Avstemning for spørsmål \'%s\' ble stengt.' % q)
    else:
        question = 'Er du sikker på at du vil avslutte spørsmål \'%s\'?' % q
        return render(request, 'genfors/confirm.html', {'question': question})
    return redirect('genfors_admin')


@login_required
def question_reset(request, question_id):
    response = question_validate(request, question_id)
    if response:
        return response

    q = Question.objects.get(id=question_id)
    if request.method == 'POST':
        q.reset_question()
        messages.success(request, 'Avstemning for spørsmål \'%s\' ble tilbakestilt.' % q)
    else:
        question = 'Er du sikker på at du vil tilbakestille spørsmål \'%s\'?' % q
        return render(request, 'genfors/confirm.html', {'question': question})
    return redirect('genfors_admin')


@login_required
def question_delete(request, question_id):
    response = question_validate(request, question_id)
    if response:
        return response

    q = Question.objects.get(id=question_id)
    if request.method == 'POST':
        messages.success(request, 'Spørsmål \'%s\' ble slettet' % q)
        q.delete()
    else:
        question = 'Er du sikker på at du vil slette spørsmål \'%s\'?' % q
        return render(request, 'genfors/confirm.html', {'question': question})
    return redirect('genfors_admin')


# Handle votes
@require_http_methods(["POST"])
@login_required
def vote(request):
    m = get_active_meeting()
    if m:
        a = anonymous_voter(request.COOKIES.get('anon_voter'), request.user.username)
        r = RegisteredVoter.objects.filter(user=request.user, meeting=m).first()

        # If user is logged in
        if a:
            return handle_user_vote(request, m, a, r)
    return HttpResponseForbidden()


@login_required
def genfors_lock_registration(request):
    if is_admin(request):
        meeting = get_active_meeting()
        if meeting:
            if request.method == 'POST':
                meeting.registration_locked = True
                meeting.save()
            else:
                question = 'Er du sikker på at du vil stenge registrering for nye brukere?'
                return render(request, 'genfors/confirm.html', {'question': question})
        else:
            messages.error(request, 'Ingen aktiv generalforsamling')
    else:
        messages.error(request, 'Du har ikke tilgang til dette')
    return redirect('genfors_admin')


@login_required
def genfors_open_registration(request):
    if is_admin(request):
        meeting = get_active_meeting()
        if meeting:
            if request.method == 'POST':
                meeting.registration_locked = False
                meeting.save()
                meeting.generate_pin_code()
            else:
                question = 'Er du sikker på at du vil åpne registrering for nye brukere?'
                description = """
Vær oppmerksom på at når man åpner registrering vil pinkoden for registrering av oppmøte forandre seg.
Du vil se den oppdaterte koden i administrasjonspanelet.
"""

                return render(request, 'genfors/confirm.html', {'question': question, 'description': description})
        else:
            messages.error(request, 'Ingen aktiv generalforsamling')
    else:
        messages.error(request, 'Du har ikke tilgang til dette')
    return redirect('genfors_admin')


@login_required
def genfors_end(request):
    if is_admin(request):
        meeting = get_next_meeting()
        if meeting:
            if request.method == 'POST':
                meeting.ended = True
                meeting.save()
                messages.success(request, 'Generalforsamlingen ble avsluttet')
            else:
                question = 'Er du sikker på at du vil avslutte generalforsamlingen?'
                return render(request, 'genfors/confirm.html', {'question': question})
        else:
            messages.error(request, 'Ingen aktiv generalforsamling')
    else:
        messages.error(request, 'Du har ikke tilgang til dette')
    return redirect('genfors_admin')


def api_admin(request):
    return HttpResponse(json.dumps({"error": "Du har ikke tilgang til dette endepunktet."}))


# Simple cached JSON Api-like endpoint to dynamically update stats via AJAX
@cache_page(5)
def api_user(request):
    m = get_active_meeting()
    reg_voter = RegisteredVoter.objects.filter(user=request.user, meeting=m).first()
    anon_voter = anonymous_voter(request.COOKIES.get('anon_voter'), request.user.username)

    if reg_voter and anon_voter:
        q = m.get_active_question()
        context = {"total_voters": m.num_can_vote()}

        if q:
            context = _handle_q(context, anon_voter, reg_voter, q)
        else:
            context["question"] = None

        return JsonResponse(context)

    else:
        return JsonResponse({"error": "Du har ikke tilgang til dette endepunktet."})


# Logs out user of genfors removing the only link between that user and the anoymous votes
def logout(request):
    if request.method == 'POST':
        response = redirect('home')
        response.delete_cookie('anon_voter')
        messages.success(request, 'Du er nå logget ut av generalforsamlingen')
        return response
    else:
        question = 'Er du sikker på at du vil logge ut?'
        description = 'Den eneste måten å logge seg inn igjen er med den personlige koden du skrev inn!'
        return render(request, 'genfors/confirm.html', {'question': question, 'description': description})


def question_validate(request, question_id):
    """
    Returns a HttpResponse if not passing validation
    """
    if is_admin(request):
        try:
            Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            messages.error(request, 'Spørsmålet finnes ikke')
            return redirect('genfors_admin')
        # Return None when passing
        return None
    else:
        messages.error(request, 'Du har ikke tilgang til dette')
    return redirect('genfors_admin')


def _handle_inactive_meeting(request):
    if get_next_meeting():
        messages.error(request, _('Den gjeldende generalforsamlingen er ikke aktiv enda eller har utgått'))
    else:
        messages.error(request, _('Det finnes ingen aktiv generalforsamling'))
    return redirect('genfors_admin')


def handle_question_admin_update(request, context, question_id):
    meeting = get_active_meeting()

    try:
        q = Question.objects.get(id=question_id, locked=False)
    except Question.DoesNotExist:
        q = Question()

    q_alt = q.get_alternatives() if q else None
    form = QuestionForm(request.POST, instance=q)
    formset = AlternativeFormSet(request.POST, queryset=q_alt)

    if form.is_valid() and formset.is_valid():
        question = form.save(commit=False)
        if not question.pk:
            question.meeting = meeting
            messages.success(request, _('Nytt spørsmål lagt til'))
        else:
            # Resetting question votes
            question.reset_question()
            messages.success(request, _('Spørsmål ble oppdatert'))
        question.save()

        if question.question_type == 1:
            formset.save(commit=False)
            # Delete forms marked for deletion
            for alternative in formset.deleted_objects:
                alternative.delete()
            # Add new
            for index, alternative in enumerate(formset.changed_objects + formset.new_objects):
                if type(alternative) is tuple:
                    # changed_objects come in the form of (object, 'changed_field')
                    alternative = alternative[0]
                alternative.question = question
                alternative.alt_id = index + 1
                alternative.save()
        return redirect('genfors_admin')
    else:
        context['form'] = form
        context['formset'] = formset
        return render(request, "genfors/question.html", context)


def handle_question_admin_detail(request, context, question_id):
    q = None
    q_alt = None
    if question_id:
        q = Question.objects.get(id=question_id, locked=False)
        if q:
            q_alt = q.get_alternatives()
        else:
            messages.error(request, 'Spørsmålet finnes ikke eller har allerede blitt stengt.')
            return redirect('genfors_admin')
    else:
        context['create'] = True
    if not q_alt:
        # If 'queryset' is None ModelFormSets will add all objects from model
        # adding .none() to make sure the form is always empty
        q_alt = Alternative.objects.none()
    context['form'] = QuestionForm(instance=q)
    context['formset'] = AlternativeFormSet(queryset=q_alt)
    return render(request, "genfors/question.html", context)


def handle_user_vote(request, m, a, r):
    """
    Handle voting for a user
    :param request: HttpRequest object
    :param m: current meeting
    :param a: anonymous user
    :param r: registered user
    :return: updated context dictionary
    """
    q = m.get_active_question()
    if not q:
        messages.error(request, 'Saken har blitt slettet')
        return redirect('genfors_index')
    if not r:
        messages.error(request, 'Du er ikke registrert som oppmøtt, og kan derfor ikke avlegge stemme.')
        return redirect('genfors_index')
    if not r.can_vote:
        messages.error(request, 'Du har ikke tilgang til å avlegge stemme')
        return redirect('genfors_index')
    # v(ote) is either AnonymousVoter or RegisterVoter
    v = a if q.anonymous else r
    if q.already_voted(v):
        messages.error(request, 'Du har allerede avlagt en stemme i denne saken.')
        return redirect('genfors_index')
    # If user is registered and has not cast a vote on the active question
    else:
        return _handle_actual_user_voting(request, q, v)


def _handle_actual_user_voting(request, q, v):
    if 'choice' in request.POST:
        alt = int(request.POST['choice'])
        if q.question_type is BOOLEAN_VOTE:
            return _handle_boolean_vote(request, alt, q, v)

        elif q.question_type is MULTIPLE_CHOICE:
            return _handle_multiple_choice_vote(request, alt, q, v)

    messages.error(
        request,
        'Det ble forsøkt å stemme på et ugyldig alternativ, stemmen ble ikke registrert.'
    )
    return redirect('genfors_index')


def _handle_boolean_vote(request, alt, q, v):
    valid = [0, 1, 2]
    if alt in valid:
        the_vote = None
        if alt == 0:
            the_vote = BooleanVote(voter=v, question=q, answer=None)
        elif alt == 1:
            the_vote = BooleanVote(voter=v, question=q, answer=True)
        elif alt == 2:
            the_vote = BooleanVote(voter=v, question=q, answer=False)
        the_vote.save()
        messages.success(request, 'Din stemme ble registrert!')
        return redirect('genfors_index')


def _handle_multiple_choice_vote(request, alt, q, v):
    alternatives = Alternative.objects.filter(question=q)
    valid = [alternative.alt_id for alternative in alternatives]
    valid.append(0)
    if alt in valid:
        if alt == 0:
            the_vote = MultipleChoice(voter=v, question=q, answer=None)
            the_vote.save()
            messages.success(request, 'Din stemme ble registrert!')
            return redirect('genfors_index')
        else:
            choice = Alternative.objects.get(alt_id=alt, question=q)
            if choice:
                the_vote = MultipleChoice(voter=v, question=q, answer=choice)
                the_vote.save()
                messages.success(request, 'Din stemme ble registrert!')
                return redirect('genfors_index')


def _handle_q(context, anon_voter, reg_voter, q):
    context["question"] = {}
    context["question"]["description"] = q.description
    context["question"]["count_blank_votes"] = q.count_blank_votes
    if q.anonymous:
        already_voted = q.already_voted(anon_voter)
    else:
        already_voted = q.already_voted(reg_voter)
    if already_voted:
        if not q.only_show_winner:
            context["question"]["results"] = q.get_results()
    context["question"]["current_votes"] = q.get_votes().count()

    if not q.only_show_winner:
        votes = q.get_votes()
        if q.anonymous:
            if q.question_type == 0:
                context["question"]["votes"] = [[str(v.voter.anonymousvoter), v.answer] for v in votes]
            elif q.question_type == 1:
                context["question"]["votes"] = [
                    [
                        str(v.voter.anonymousvoter),
                        v.answer.description
                    ] if v.answer else [
                        str(v.voter.anonymousvoter),
                        "Blankt"
                    ] for v in votes
                ]

            # Shuffle the order of votes so you cannot infer who cast what vote when there are few voters left
            random.shuffle(context['question']['votes'])

        else:
            if q.question_type == 0:
                context["question"]["votes"] = [[str(v.voter.registeredvoter), v.answer] for v in votes]
            elif q.question_type == 1:
                context["question"]["votes"] = [
                    [
                        str(v.voter.registeredvoter),
                        v.answer.description
                    ] if v.answer else [
                        str(v.voter.registeredvoter),
                        "Blankt"
                    ] for v in votes
                ]
    return context
