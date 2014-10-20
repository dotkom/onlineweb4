# -*- encoding: utf-8 -*-

from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required

from apps.dashboard.tools import has_access

@login_required
def index(request):
    """
    This is the main dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    perms = request.user.get_group_permissions()

    return render(request, 'dashboard.html', {'user_permissions': perms})
