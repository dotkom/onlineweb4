# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from apps.approval.models import MembershipApproval
from apps.authentication.models import AllowedUsername


@ensure_csrf_cookie
@login_required
def index(request):
    context = {}
    context['membership_applications'] = MembershipApproval.objects.filter(processed=False)
    
    return render(request, 'approval/dashboard/index.html', context)


@ensure_csrf_cookie
@login_required
def approve_application(request):
    if request.is_ajax():
        if request.method == 'POST':
            application_id = request.POST.get('application_id')
            app = get_object_or_404(MembershipApproval, pk=application_id)

            if app.processed:
                messages.error(request, _(u"Denne søknaden er allerede behandlet."))
                return redirect(index)

            user = app.applicant

            if not user.ntnu_username:
                messages.error(request, _(u"Brukeren (%s) har ikke noe lagret ntnu brukernavn.") % user.get_full_name())
                return redirect(index)

            if app.is_fos_application():
                user.field_of_study = app.field_of_study
                user.started_date = app.started_date
                user.save()

            if app.is_membership_application():
                membership = AllowedUsername.objects.filter(username = user.ntnu_username)
                if membership.count() == 1:
                    membership = membership[0]
                    membership.expiration_date = app.new_expiry_date
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
                    membership.description = """Added by approvals app.

Approved by %s on %s.""" % (request.user.get_full_name(), str(timezone.now().date()))
                    membership.save()

            app.processed = True
            app.approver = request.user
            app.processed_date = timezone.now()
            app.save()

            return HttpResponse(status=200)

    raise Http404


@login_required
def decline_application(request):
    

    return redirect(index)
