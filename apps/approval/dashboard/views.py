# -*- encoding: utf-8 -*-

import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from guardian.decorators import permission_required

from apps.approval.models import MembershipApproval
from apps.authentication.models import AllowedUsername
from apps.dashboard.tools import has_access, get_base_context


@ensure_csrf_cookie
@login_required
@permission_required('approval.view_membershipapproval', return_403=True)
def index(request):

    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context['membership_applications'] = MembershipApproval.objects.filter(processed=False)
    context['processed_applications'] = MembershipApproval.objects.filter(
        processed=True
    ).order_by('-processed_date')[:10]

    return render(request, 'approval/dashboard/index.html', context)


@ensure_csrf_cookie
@login_required
@permission_required('approval.change_membershipapproval', return_403=True)
def approve_application(request):
    if request.is_ajax():
        if request.method == 'POST':
            application_id = request.POST.get('application_id')
            apps = MembershipApproval.objects.filter(pk=application_id)

            if apps.count() == 0:
                response_text = json.dumps({'message': _(
                    u"""Kan ikke finne en søknad med denne IDen (%s).
Om feilen vedvarer etter en refresh, kontakt dotkom@online.ntnu.no.""") % application_id})
                return HttpResponse(status=412, content=response_text)

            app = apps[0]

            if app.processed:
                response_text = json.dumps({'message': _(u"Denne søknaden er allerede behandlet.")})
                return HttpResponse(status=412, content=response_text)

            user = app.applicant

            if not user.ntnu_username:
                response_text = json.dumps({'message': _(
                    u"""Brukeren (%s) har ikke noe lagret ntnu brukernavn.""") % user.get_full_name()})
                return HttpResponse(status=412, content=response_text)

            if app.is_fos_application():
                user.field_of_study = app.field_of_study
                user.started_date = app.started_date
                user.save()

            if app.is_membership_application():
                membership = AllowedUsername.objects.filter(username=user.ntnu_username)
                if membership.count() == 1:
                    membership = membership[0]
                    membership.expiration_date = app.new_expiry_date
                    if not membership.description:
                        membership.description = ''
                    membership.description += """
-------------------
Updated by approvals app.

Approved by %s on %s.

Old notes:
%s
""" % (request.user.get_full_name(), str(timezone.now().date()), membership.note)
                    membership.note = user.get_field_of_study_display() + " " + str(user.started_date)
                    membership.save()
                else:
                    membership = AllowedUsername()
                    membership.username = user.ntnu_username
                    membership.expiration_date = app.new_expiry_date
                    membership.registered = timezone.now().date()
                    membership.note = user.get_field_of_study_display() + " " + str(user.started_date)
                    membership.description = u"""Added by approvals app.

Approved by %s on %s.""" % (request.user.get_full_name(), str(timezone.now().date()))
                    membership.save()

            app.processed = True
            app.processed_date = timezone.now()
            app.approved = True
            app.approver = request.user
            app.save()

            return HttpResponse(status=200)

    raise Http404


@login_required
@ensure_csrf_cookie
@permission_required('approval.change_membershipapproval', return_403=True)
def decline_application(request):
    if request.is_ajax():
        if request.method == 'POST':
            application_id = request.POST.get('application_id')
            apps = MembershipApproval.objects.filter(pk=application_id)

            if apps.count() == 0:
                response_text = json.dumps({'message': _(u"""
Kan ikke finne en søknad med denne IDen (%s).
Om feilen vedvarer etter en refresh, kontakt dotkom@online.ntnu.no.""") % application_id})
                return HttpResponse(status=412, content=response_text)

            app = apps[0]

            if app.processed:
                response_text = json.dumps({'message': _(u"Denne søknaden er allerede behandlet.")})
                return HttpResponse(status=412, content=response_text)

            message = request.POST.get('message')

            app.processed = True
            app.processed_date = timezone.now()
            app.approved = False
            app.approver = request.user
            app.message = message
            app.save()

            return HttpResponse(status=200)

    raise Http404
