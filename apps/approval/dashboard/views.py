# -*- encoding: utf-8 -*-

from django.shortcuts import render

from apps.approval.models import MembershipApproval

def index(request):
    context = {}
    context['membership_applications'] = MembershipApproval.objects.filter(processed=False)
    
    return render(request, 'approval/dashboard/index.html', context)

def approve_application(request, application_id):
    print "booya"

    return render(request, 'approval/dashboard/index.html', {})

def decline_application(request, application_is):
    print "booya"

    return render(request, 'approval/dashboard/index.html', {})
