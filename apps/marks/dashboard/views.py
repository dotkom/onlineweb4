# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required
from apps.dashboard.tools import has_access, get_base_context
from django.shortcuts import render, get_object_or_404

@login_required
def index(request):
    """
    Marks overview
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'marks/dashboard/index.html', context)


@login_required
@permission_required('auth.change_group', return_403=True)
def marks_new(request):
    """
    Here
    """

    context = get_base_context(request)

    return render(request, 'marks/dashboard/marks_new.html', context)
