# -*- encoding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

from guardian.decorators import permission_required

def index(request):
    """
    This is the main dashboard view
    """

    try:
        committees = Group.objects.get(name='Komiteer')
    except ObjectDoesNotExist:
        committees = None

    if not request.user.is_superuser:
        if not committees or committees not in request.user.groups.all():
            raise PermissionDenied

    perms = list(request.user.get_group_permissions())
    perms.sort()

    return render(request, 'dashboard.html', {'user_permissions': perms})
