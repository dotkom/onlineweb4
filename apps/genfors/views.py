#-*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.http import require_http_methods
from apps.genfors.forms import LoginForm, MeetingForm, QuestionForm, RegisterVoterForm, AlternativeFormSet
from apps.genfors.models import Meeting, Question, RegisteredVoter, AnonymousVoter, Alternative, BooleanVote, MultipleChoice
from apps.genfors.models import BOOLEAN_VOTE, MULTIPLE_CHOICE
from hashlib import sha256
import datetime
import json


@login_required
def genfors(request):
    context = {}
    meeting = get_active_meeting()

    # Check for active meeting
    if not meeting:
        return render(request, "genfors/index.html", context)

    # Check for session voter object
    if is_registered(request):
        context['meeting'] = meeting

        # If there is an active question
        aq = meeting.get_active_question()
        if aq:
            reg_voter = RegisteredVoter.objects.filter(user=request.user, meeting=meeting)
            anon_voter = AnonymousVoter.objects.get(id=request.session.get('anon_voter'))
            if reg_voter:
                reg_voter = reg_voter[0]

                if aq.anonymous:
                    context['already_voted'] = aq.already_voted(anon_voter)
                else:
                    context['already_voted'] = aq.already_voted(reg_voter)
            else:
                reg_voter = None

            total_votes = aq.get_votes().count()
            alternatives = aq.get_alternatives()

            context['active_question'] = {}
            context['active_question']['total_votes'] = total_votes
            context['active_question']['alternatives'] = alternatives

            context['registered_voter'] = reg_voter
            context['anonymous_voter'] = anon_voter

            res = aq.get_results()

            if aq.question_type is BOOLEAN_VOTE and total_votes != 0:
                context['active_question']['yes_percent'] = res['JA'] * 100 / total_votes
                context['active_question']['no_percent'] = res['NEI'] * 100 / total_votes
                context['active_question']['blank_percent'] = res['BLANKT'] * 100 / total_votes

            elif aq.question_type is MULTIPLE_CHOICE and total_votes != 0:
                context['active_question']['multiple_choice'] = {a.description: [0, 0] for a in alternatives}
                context['active_question']['multiple_choice']['Blankt'] = [0, 0]
                for k, v in res.items():
                    context['active_question']['multiple_choice'][k] = [v, v * 100 / total_votes]

        return render(request, "genfors/index.html", context)

    # If user is not logged in
    else:
        # Process stuff from the login form
        if request.method == 'POST' and not meeting.registration_locked:
            form = RegisterVoterForm(request.POST)
            context['form'] = form
            if form.is_valid():
                # Creating hash
                h = sha256()
                h.update(settings.SECRET_KEY)
                h.update(request.user.username)
                h.update(form.cleaned_data['salt'])
                h = h.hexdigest()
                # Create a registered voter object if it does not already exist
                reg_voter = RegisteredVoter.objects.filter(meeting=meeting, user=request.user)
                if not reg_voter:
                    reg_voter = RegisteredVoter(user=request.user, meeting=meeting)
                    reg_voter.save()
                    anon_voter = AnonymousVoter(user_hash=h, meeting=meeting)
                    anon_voter.save()
                else:
                    try:
                        anon_voter = AnonymousVoter.objects.get(user_hash=h, meeting=meeting)
                    except AnonymousVoter.DoesNotExist:
                        messages.error(request, _(u'Feil personlig kode'))
                        anon_voter = None
                if anon_voter:
                    request.session['anon_voter'] = anon_voter.id
                elif 'anon_voter' in request.session:
                    del request.session['anon_voter']
                return redirect('genfors_index')

        # Set registration_locked context and create login form
        else:
            context['form'] = RegisterVoterForm()
            if meeting:
                context['registration_locked'] = meeting.registration_locked
            else:
                context['registration_locked'] = True

    return render(request, "genfors/index_login.html", context)


@login_required
def registered_voters(request):
    context = {}
    if is_admin(request):
        meeting = get_active_meeting()
        if meeting:
            context['registered_voters'] = meeting.get_attendee_list()
    return render(request, "genfors/registered_voters.html", context)


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
        elif request.method == 'POST':
            form = MeetingForm(request.POST)
            context['form'] = form
            if form.is_valid():
                meeting = Meeting(title=form.cleaned_data['title'],
                                  start_date=form.cleaned_data['start_date'])
                meeting.save()
                messages.success(request, _(u'Generalforsamling lagt til'))
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
                messages.error(request, _(u'Den gjeldende generalforsamlingen er ikke aktiv enda eller har utgått'))
            else:
                messages.error(request, _(u'Det finnes ingen aktiv generalforsamling'))
            return redirect('genfors_admin')
        if question_id is None and meeting.get_active_question():
            messages.error(request, _(u'Kan ikke legge til et nytt spørsmål når det allerede er et aktivt et'))
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
                    messages.success(request, _(u'Nytt spørsmål lagt til'))
                else:
                    # Resetting question votes
                    question.reset_question()
                    messages.success(request, _(u'Spørsmål ble oppdatert'))
                question.save()
                print type(question.question_type)
                if question.question_type == 1:
                    alternatives = formset.save(commit=False)
                    # # Add new
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
                    form = QuestionForm(instance=q)
                    formset = AlternativeFormSet(queryset=q.get_alternatives())
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
                json_response['can_vote': user.can_vote]
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
    if request.method == 'POST':
        q.set_result_and_lock()
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
        # If user is logged in
        if is_registered(request):
            q = m.get_active_question()
            a = AnonymousVoter.objects.get(id=request.session.get('anon_voter'))
            r = RegisteredVoter.objects.filter(user=request.user, meeting=m)
            if r:
                r = r[0]
            else:
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
                            vote = None
                            if alt == 0:
                                vote = BooleanVote(voter=v, question=q, answer=None)
                            elif alt == 1:
                                vote = BooleanVote(voter=v, question=q, answer=True)
                            elif alt == 2:
                                vote = BooleanVote(voter=v, question=q, answer=False)
                            vote.save()
                            messages.success(request, 'Din stemme ble registrert!')
                            return redirect('genfors_index')

                    elif q.question_type is MULTIPLE_CHOICE:
                        alternatives = Alternative.objects.filter(question=q)
                        valid = [a.alt_id for a in alternatives]
                        valid.append(0)
                        if alt in valid:
                            vote = None
                            if alt == 0:
                                vote = MultipleChoice(voter=v, question=q, answer=None)
                                vote.save()
                                messages.success(request, 'Din stemme ble registrert!')
                                return redirect('genfors_index')
                            else:
                                choice = Alternative.objects.get(alt_id=alt, question=q)
                                if choice:
                                    vote = MultipleChoice(voter=v, question=q, answer=choice)
                                    vote.save()
                                    messages.success(request, 'Din stemme ble registrert!')
                                    return redirect('genfors_index')

                messages.error(request, 'Det ble forsøkt å stemme på et ugyldig alternativ, stemmen ble ikke registrert.')
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
            else:
                question = 'Er du sikker på at du vil åpne registrering for nye brukere?'
                return render(request, 'genfors/confirm.html', {'question': question})
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


def get_active_meeting():
    today = datetime.date.today()
    meetings = Meeting.objects.filter(start_date__range=[today, today + datetime.timedelta(hours=24)], ended=False).order_by('-start_date')
    if meetings:
        return meetings[0]


def get_next_meeting():
    today = datetime.date.today()
    meetings = Meeting.objects.filter(ended=False).order_by('-start_date')
    if meetings:
        return meetings[0]


# Helper function
def is_admin(request):
    return request.session.get('genfors_admin') is True


def is_registered(request):
    try:
        av = AnonymousVoter.objects.get(id=request.session.get('anon_voter'))
    except AnonymousVoter.DoesNotExist:
        return False
    if type(av) is AnonymousVoter:
        if av.meeting == get_active_meeting():
            return True
        else:
            # RegisteredVoter object is for an older genfors
            del request.session['anon_voter']
            return False
    return False


def question_validate(request, question_id):
    """Returns a HttpResponse if not passing validation"""
    if is_admin(request):
        try:
            q = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            messages.error(request, 'Spørsmålet finnes ikke')
            return redirect('genfors_admin')
        # Return None when passing
        return None
    else:
        messages.error(request, 'Du har ikke tilgang til dette')
    return redirect('genfors_admin')
