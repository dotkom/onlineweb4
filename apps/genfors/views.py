# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from apps.genfors.forms import LoginForm, MeetingForm, QuestionForm, RegisterVoterForm, AlternativeFormSet
from apps.genfors.models import (
    Meeting,
    Question,
    RegisteredVoter,
    AnonymousVoter,
    Alternative,
    BooleanVote,
    MultipleChoice,
    Result
)
from apps.genfors.models import BOOLEAN_VOTE, MULTIPLE_CHOICE
from hashlib import sha256
import datetime
import json
import random


@login_required
def genfors(request):
    context = {}
    meeting = get_active_meeting()

    # Check for active meeting
    if not meeting:
        return render(request, "genfors/index.html", context)

    reg_voter = RegisteredVoter.objects.filter(user=request.user, meeting=meeting).first()
    anon_voter = anonymous_voter(request.COOKIES.get('anon_voter'), request.user.username)

    # Check for cookie voter hash
    if anon_voter:
        context['meeting'] = meeting
        context['registered_voter'] = reg_voter

        # If there is an active question
        aq = meeting.get_active_question()
        if aq:
            if aq.anonymous:
                context['already_voted'] = aq.already_voted(anon_voter)
            else:
                context['already_voted'] = aq.already_voted(reg_voter)

            total_votes = aq.get_votes().count()
            alternatives = aq.get_alternatives()

            context['active_question'] = {}
            context['active_question']['total_votes'] = total_votes
            context['active_question']['alternatives'] = alternatives

            context['registered_voter'] = reg_voter
            context['anonymous_voter'] = anon_voter

            res = aq.get_results()

            if total_votes != 0 and not aq.only_show_winner:
                if aq.question_type is BOOLEAN_VOTE:
                    context['active_question']['yes_percent'] = res['data']['Ja'] * 100 // total_votes
                    context['active_question']['no_percent'] = res['data']['Nei'] * 100 // total_votes
                    context['active_question']['blank_percent'] = res['data']['Blankt'] * 100 // total_votes

                elif aq.question_type is MULTIPLE_CHOICE and total_votes != 0:
                    context['active_question']['multiple_choice'] = {}
                    for a in alternatives:
                        context['active_question']['multiple_choice'][a.description] = [0, 0]
                    context['active_question']['multiple_choice']['Blankt'] = [0, 0]
                    for k, v in res['data'].items():
                        context['active_question']['multiple_choice'][k] = [v, v * 100 // total_votes]
        return render(request, "genfors/index.html", context)

    # If user is not logged in
    else:
        # Process stuff from the login form
        if request.method == 'POST' and (reg_voter or not meeting.registration_locked):
            form = RegisterVoterForm(request.POST)
            context['form'] = form
            if form.is_valid():
                # Creating hash
                h = sha256()
                h.update(settings.SECRET_KEY.encode('utf-8'))
                h.update(request.user.username.encode('utf-8'))
                h.update(form.cleaned_data['salt'].encode('utf-8'))
                h = h.hexdigest()
                # Create a registered voter object if it does not already exist
                reg_voter = RegisteredVoter.objects.filter(meeting=meeting, user=request.user)
                if not reg_voter:
                    reg_voter = RegisteredVoter(user=request.user, meeting=meeting)
                    reg_voter.save()
                    # Double hashing when saving while we store the original hash as a cookie
                    h2 = sha256()
                    h2.update(h)
                    h2.update(request.user.username)
                    anon_voter = AnonymousVoter(user_hash=h2.hexdigest(), meeting=meeting)
                    anon_voter.save()
                else:
                    # Trying to get anonymous voter object too, if not found the secret code was wrong
                    anon_voter = anonymous_voter(h, request.user.username)
                    if not anon_voter:
                        messages.error(request, _('Feil personlig kode'))
                response = redirect('genfors_index')
                if anon_voter:
                    # Anyonous voter hash stored in cookies for 1 day
                    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                    response.set_cookie('anon_voter', h, expires=tomorrow)
                elif 'anon_voter' in request.COOKIES:
                    # Delete old hash
                    response.delete_cookie('anon_voter')
                return response
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
            context['meeting'] = meeting
            context['question'] = meeting.get_active_question()
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
            if get_next_meeting():
                messages.error(request, _('Den gjeldende generalforsamlingen er ikke aktiv enda eller har utgått'))
            else:
                messages.error(request, _('Det finnes ingen aktiv generalforsamling'))
            return redirect('genfors_admin')
        if question_id is None and meeting.get_active_question():
            messages.error(request, _('Kan ikke legge til et nytt spørsmål når det allerede er et aktivt et'))
            return redirect('genfors_admin')
        if request.method == 'POST':
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
        else:
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
                if 'choice' in request.POST:
                    alt = int(request.POST['choice'])
                    if q.question_type is BOOLEAN_VOTE:
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

                    elif q.question_type is MULTIPLE_CHOICE:
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

                messages.error(
                    request,
                    'Det ble forsøkt å stemme på et ugyldig alternativ, stemmen ble ikke registrert.'
                )
                return redirect('genfors_index')

        # Else forbid
        return HttpResponse(status_code=403, reason_phrase='Forbidden')
    else:
        return HttpResponse(status_code=403, reason_phrase='Forbidden')


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
            context["question"] = {}
            context["question"]["description"] = q.description
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
                        genfors["question"]["votes"] = [[str(v.voter.anonymousvoter), v.answer] for v in votes]
                    elif q.question_type == 1:
                        genfors["question"]["votes"] = [
                            [
                                str(v.voter.anonymousvoter),
                                v.answer.description
                            ] if v.answer else [
                                str(v.voter.anonymousvoter),
                                "Blankt"
                            ] for v in votes
                        ]

                    # Shuffle the order of votes so you cannot infer who cast what vote when there are few voters left
                    random.shuffle(genfors['question']['votes'])

                else:
                    if q.question_type == 0:
                        genfors["question"]["votes"] = [[str(v.voter.registeredvoter), v.answer] for v in votes]
                    elif q.question_type == 1:
                        genfors["question"]["votes"] = [
                            [
                                str(v.voter.registeredvoter),
                                v.answer.description
                            ] if v.answer else [
                                str(v.voter.registeredvoter),
                                "Blankt"
                            ] for v in votes
                        ]
        else:
            genfors["question"] = None

        return JsonResponse(genfors)

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

# Helper functions


def get_active_meeting():
    today = datetime.date.today()
    hour24 = datetime.timedelta(hours=24)
    return Meeting.objects.filter(
        start_date__lte=timezone.now(), ended=False,
        start_date__range=[today - hour24, today + hour24]
    ).order_by('-start_date').first()


def get_next_meeting():
    return Meeting.objects.filter(ended=False).order_by('-start_date').first()


# Helper function
def is_admin(request):
    return request.session.get('genfors_admin') is True


def anonymous_voter(anon_cookie, username):
    """Returns anon voter object if found"""
    if not anon_cookie:
        # Empty cookie
        return
    meeting = get_active_meeting()
    # Hashing with username before lookup
    h = sha256()
    h.update(anon_cookie.encode('utf-8'))
    h.update(username.encode('utf-8'))
    return AnonymousVoter.objects.filter(user_hash=h.hexdigest(), meeting=meeting).first()


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
