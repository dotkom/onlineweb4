# -*- encoding: utf-8 -*-

import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from apps.approval.forms import FieldOfStudyApplicationForm
from apps.approval.models import MembershipApproval, FieldOfStudyApproval 
from apps.authentication.models import get_length_of_field_of_study

@login_required
def index(request):
    return render(request, 'approval/index.html', {})

@login_required
def create_fos_application(request):
    if request.method == 'POST':
        form = FieldOfStudyApplicationForm(request.POST)
        if form.is_valid(): 
            cleaned = form.cleaned_data
            
            started_day = 1
            started_month = 0
            started_year = int(cleaned['started_year'])

            if cleaned['started_semester'] == "h":
                started_month = 7
            if cleaned['started_semester'] == "v":
                started_month = 1
            
            started_date = datetime.date(started_year, started_month, started_day)
            field_of_study = int(cleaned['field_of_study'])
            
            # Does the user already have a field of study and started date?
            if request.user.started_date and request.user.field_of_study:
                # If there is no change from the current settings, ignore the request
                if request.user.started_date == started_date and request.user.field_of_study == field_of_study:
                    messages.error(request, _(u"Du er allerede registrert med denne studieretningen og denne startdatoen."))
                    redirect('profiles')

            fos_application = FieldOfStudyApproval(
                applicant = request.user,
                field_of_study = field_of_study,
                started_date = started_date
            )
            fos_application.save()

            length_of_fos = get_length_of_field_of_study(field_of_study)
            if length_of_fos > 0:
                membership_application = MembershipApproval(
                    applicant = request.user,
                    # Expiry dates should be 15th September, so that we have tiem to get new lists from NTNU
                    new_expiry_date = datetime.date(started_year, 9, 15) + datetime.timedelta(days=365*length_of_fos)
                ) 
                membership_application.save()

    return redirect('profiles')

@login_required
def create_membership_application(request):
    pass

