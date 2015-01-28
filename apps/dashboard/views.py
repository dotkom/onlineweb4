# -*- encoding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.dashboard.tools import has_access, get_base_context


@login_required
def index(request):
    """
    This is the main dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'dashboard/dashboard.html', context)
