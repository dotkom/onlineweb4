#-*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.genfors.forms import LoginForm
from apps.genfors.models import Meeting

import datetime


@login_required
def genfors(request):
    context = {}
    today = datetime.date.today()

    meetings = Meeting.objects.filter(start_date__range=[today, today + datetime.timedelta(days=1)]).order_by('-start_date')
    if meetings:
        meeting = meetings[0]
        context['meeting'] = meeting
    return render(request, "genfors/index.html", context)


@login_required
def admin(request):
    context = {}
    # Check if user is logged in as genfors admin
    if request.session.get('genfors_admin') == True:
        meetings = Meeting.objects.filter(registration_locked=False).order_by('-start_date')
        if meetings:
            meeting = meetings[0]
            context['meeting'] = meeting
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
