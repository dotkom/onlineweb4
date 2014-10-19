# -*- encoding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.models import Permission, Group

from guardian.decorators import permission_required

@permission_required('approval.view_membershipapproval', return_403=True)
def index(request):
    """
    This is the main dashboard view
    """

    perms = list(request.user.get_group_permissions())
    perms.sort()

    return render(request, 'dashboard.html', {'user_permissions': perms})
