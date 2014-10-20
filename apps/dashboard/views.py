# -*- encoding: utf-8 -*-

from django.shortcuts import render
from django.core.exceptions import PermissionDenied

from guardian.decorators import permission_required

from apps.dashboard.tools import has_access

def index(request):
    """
    This is the main dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    perms = request.user.get_group_permissions()

    return render(request, 'dashboard.html', {'user_permissions': perms})
