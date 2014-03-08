#-*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import json
from apps.genfors.forms import LoginForm, MeetingForm, QuestionForm, RegisterVoterForm, AlternativeFormSet
from apps.genfors.models import Meeting, Question, RegisteredVoter
import datetime


@login_required
def genfors(request):
    context = {}
    meeting = get_active_meeting()
    if request.session.get('registered_voter') == True:
        if meeting:
            context['meeting'] = meeting
            if meeting.get_active_question():
                aq = meeting.get_active_question()
                context['active_question'] = {}
                context['active_question']['total_votes'] = aq.get_votes().count()
                res = aq.get_results()
                if aq.question_type == 0 and context['active_question']['total_votes'] != 0:
                    context['active_question']['yes_percent'] = res['JA'] * 100 / context['active_question']['total_votes']
                    context['active_question']['no_percent'] = res['NEI'] * 100 / context['active_question']['total_votes']
                    context['active_question']['blank_percent'] = res['BLANKT'] * 100 / context['active_question']['total_votes']
                elif aq.question_type == 1 and context['active_question']['total_votes'] != 0:
                    context['active_question']['multiple_choice']
                    context['active_question']['multiple_choice'] = [sum(res[r] * 100 / context['active_question']['total_votes']) for r in res]
        return render(request, "genfors/index.html", context)
    else:
        if request.method == 'POST' and not meeting.registration_locked:
            form = RegisterVoterForm(request.POST)
            context['form'] = form
            if form.is_valid():
                request.session['registered_voter'] = True
                return redirect('genfors_index')
        else:
            context['form'] = RegisterVoterForm()
            context['registration_locked'] = meeting.registration_locked
    return render(request, "genfors/index_login.html", context)


@login_required
def registered_voters(request):
    context = {}
    if request.session.get('genfors_admin') is True:
        meeting = get_active_meeting()
        if meeting:
            context['registered_voters'] = meeting.get_attendee_list()
    return render(request, "genfors/registered_voters.html", context)


@login_required
def admin(request):
    context = {}
    # Check if user is logged in as genfors admin
    if request.session.get('genfors_admin') is True:
        meeting = get_next_meeting()
        if meeting:
            context['meeting'] = meeting
            question = meeting.get_active_question()
            if question:
                context['question'] = question
            else:
                if request.method == 'POST':
                    form = QuestionForm(request.POST)
                    if form.is_valid():
                        data = form.cleaned_data
                        question = Question(meeting=meeting, anonymous=data['anonymous'],
                                            question_type=data['anonymous'], description=data['description'],
                                            number_of_alternatives=data['number_of_alternatives'])
                        question.save()
                        messages.success(request, _(u'Nytt spørsmål lagt til'))
                        return redirect('genfors_admin')
                else:
                    form = QuestionForm()
                    formset = AlternativeFormSet()
                context['form'] = form
                context['formset'] = formset
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
    if 'genfors_admin' in request.session:
        del request.session['genfors_admin']
    return redirect('genfors_index')

@require_http_methods(["POST"])
def vote(request):
    meetings = Meeting.objects.filter(registration_locked=False).order_by('-start_date')
    if meetings:
        m = meetings[0]
        data = json.decode(request.body)
        if not RegisteredVoter.objects.filter(user=request.user, meeting=m):
            return HttpResponse(status_code=403, reason_phrase='Forbidden')
    else:
        return HttpResponse(status_code=403, reason_phrase='Forbidden')


def get_active_meeting():
    today = datetime.date.today()
    meetings = Meeting.objects.filter(start_date__range=[today, today + datetime.timedelta(days=1)]).order_by('-start_date')
    if meetings:
        return meetings[0]


def get_next_meeting():
    today = datetime.date.today()
    meetings = Meeting.objects.filter(registration_locked=False, start_date__gt=today).order_by('-start_date')
    if meetings:
        return meetings[0]
