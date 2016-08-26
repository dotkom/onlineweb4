# -*- encoding: utf-8 -*-

import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.approval.forms import FieldOfStudyApplicationForm
from apps.approval.models import MembershipApproval
from apps.authentication.models import AllowedUsername, get_length_of_field_of_study


@login_required
def create_fos_application(request):
    if request.method == 'POST':
        if not request.user.ntnu_username:
            messages.error(request, _("Du må knytte et NTNU-brukernavn til kontoen din."))
            return redirect('profiles_active', active_tab='membership')

        form = FieldOfStudyApplicationForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data

            field_of_study = int(cleaned['field_of_study'])

            if field_of_study == 0:
                messages.warning(request, _("Denne studieretningen (Gjest) er ikke et gyldig alternativ."))
                return redirect('profiles_active', active_tab='membership')

            started_day = 1
            started_month = 0
            started_year = int(cleaned['started_year'])

            if cleaned['started_semester'] == "h":
                started_month = 7
            if cleaned['started_semester'] == "v":
                started_month = 1

            started_date = datetime.date(started_year, started_month, started_day)

            # Does the user already have a field of study and started date?
            if request.user.started_date and request.user.field_of_study:
                # If there is no change from the current settings, ignore the request
                if request.user.started_date == started_date and request.user.field_of_study == field_of_study:
                    messages.error(
                        request,
                        _("Du er allerede registrert med denne studieretningen og denne startdatoen.")
                    )
                    return redirect('profiles_active', active_tab='membership')

            application = MembershipApproval(
                applicant=request.user,
                field_of_study=field_of_study,
                started_date=started_date
            )

            length_of_fos = get_length_of_field_of_study(field_of_study)
            if length_of_fos > 0:
                application.new_expiry_date = get_expiry_date(started_year, length_of_fos)
            application.save()

            messages.success(request, _("Søknad om bytte av studieretning er sendt."))

        return redirect('profiles_active', active_tab='membership')
    raise Http404


def get_expiry_date(started_year, length_of_fos):
    today = timezone.now().date()
    # Expiry dates should be 15th September, so that we have time to get new lists from NTNU
    new_expiry_date = datetime.date(
        started_year, 9, 16) + datetime.timedelta(days=365*length_of_fos)
    # Expiry dates in the past sets the expiry date to next september
    if new_expiry_date < today:
        if today < datetime.date(today.year, 9, 15):
            new_expiry_date = datetime.date(today.year, 9, 15)
        else:
            new_expiry_date = datetime.date(
                today.year, 9, 16) + datetime.timedelta(days=365)
    return new_expiry_date


@login_required
def create_membership_application(request):
    if request.method == 'POST':
        if not request.user.has_expiring_membership:
            messages.error(request, _("Din bruker har ikke et utløpende medlemskap."))
            return redirect('profiles_active', active_tab='membership')

        if not request.user.ntnu_username:
            messages.error(request, _("Du må knytte et NTNU-brukernavn til kontoen din."))
            return redirect('profiles_active', active_tab='membership')

        # Extend length of membership by 1 year
        membership = AllowedUsername.objects.get(username=request.user.ntnu_username)
        new_expiration_date = datetime.date(membership.expiration_date.year + 1, 9, 16)

        application = MembershipApproval(
            applicant=request.user,
            field_of_study=request.user.field_of_study,
            new_expiry_date=new_expiration_date,
        )
        application.save()

        messages.success(request, _("Søknad om ett års forlenget medlemskap er sendt."))

        return redirect('profiles_active', active_tab='membership')
    raise Http404


@login_required
def cancel_application(request, application_id):
    app = get_object_or_404(MembershipApproval, pk=application_id)

    if app.applicant != request.user:
        messages.error(request, _("Bare søkeren selv kan slette en søknad."))
        return redirect('profiles_active', active_tab='membership')

    if app.processed:
        messages.error(request, _("Denne søknaden er behandlet og kan ikke slettes."))
        return redirect('profiles_active', active_tab='membership')

    app.delete()

    return redirect('profiles_active', active_tab='membership')
