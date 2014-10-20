# -*- encoding: utf-8 -*-

from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from guardian.decorators import permission_required

from apps.dashboard.tools import has_access, get_base_context
from apps.approval.models import MembershipApproval

@login_required
def index(request):
    """
    This is the main dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'dashboard/dashboard.html', context)

# Group module views

@login_required
def group_index(request):
    """
    Group module in dashboard that lists groups.
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    context['groups'] = Group.objects.all().order_by('name')

    return render(request, 'dashboard/groups.html', context)
