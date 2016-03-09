# -*- encoding: utf-8 -*-

from apps.dashboard.tools import get_base_context, has_access
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


@login_required
def index(request):
    """
    This is the main dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'dashboard/dashboard.html', context)
