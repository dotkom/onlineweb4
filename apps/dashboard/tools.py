# -*- encoding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

from apps.approval.models import MembershipApproval


def has_access(request):
    """
    This helper method does a basic check to see if the logged in user
    has access to the dashboard.

    We might add additional checks here later.
    """

    if request.user.is_superuser:
        return True

    try:
        committees = Group.objects.get(name='Komiteer')
    except ObjectDoesNotExist:
        committees = None

    if committees and committees in request.user.groups.all():
        return True

    return False


def get_base_context(request):
    """
    This function returns a dictionary with the proper context variables
    needed for given permission settings. Should be used as the initial
    context for every dashboard view. For example, it is used for rendering
    badges in the dashboard menu.

    Add your own if req.user.has_perm statements adding the context objects
    of that you need.
    """

    context = {}

    context['user_permissions'] = set(request.user.get_all_permissions())

    # Check if we need approval count to display in template sidebar badge
    if request.user.has_perm('approval.view_membershipapproval'):
        context['approval_pending'] = MembershipApproval.objects.filter(
            processed=False).count()

    return context
