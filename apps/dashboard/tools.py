# -*- encoding: utf-8 -*-

from datetime import date

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.models import Group

from guardian.mixins import PermissionRequiredMixin

from apps.approval.models import MembershipApproval
from apps.inventory.models import Batch
from apps.posters.models import Poster


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


def check_access_or_403(request):
    """
    Checks if a user bundled in a request object has access using has_access
    tool function, if not raise a 403 exception
    """
    if not has_access(request):
        raise PermissionDenied


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

    # Check if there exists a batch in inventory that has expired
    if request.user.has_perm('inventory.view_item'):
        if Batch.objects.filter(expiration_date__lt=date.today()):
            context['inventory_expired'] = True

    if request.user.has_perm('posters.view_poster'):
        if Poster.objects.filter(assigned_to=None) or Poster.objects.filter(assigned_to=request.user):
            context['poster_orders'] = Poster.objects.filter(assigned_to=None).count() + \
                                       Poster.objects.filter(assigned_to=request.user, finished=False).count()

    return context


# Mixin for Class Based Views
class DashboardMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not has_access(self.request):
            raise PermissionDenied
        return super(DashboardMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardMixin, self).get_context_data(**kwargs)
        context.update(get_base_context(self.request))
        return context


class DashboardPermissionMixin(DashboardMixin, PermissionRequiredMixin):
    return_403 = True
