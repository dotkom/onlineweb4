# -*- encoding: utf-8 -*-

from datetime import date

from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from guardian.mixins import PermissionRequiredMixin

from apps.approval.models import MembershipApproval
from apps.gallery.models import UnhandledImage
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
            context['poster_orders'] = Poster.objects.filter(assigned_to=None).count()
            context['poster_orders'] += Poster.objects.filter(assigned_to=request.user, finished=False).count()

    # Check if we have any unhandled images pending crop and save
    if request.user.has_perm('gallery.view_unhandledimage'):
        context['unhandled_images'] = UnhandledImage.objects.all()

    return context


# Mixin for Class Based Views
class DashboardMixin(object):
    """
    The DashboardMixin sets up the needed context data, as well as performs
    generic access checks.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Hooks into the dispatch cycle, checking whether or not the currently
        logged in user has access to the dashboard in general.
        :param request: Django Request object
        :param args: Positional arguments
        :param kwargs: Keyword arguments
        :return: Invocation of superclass dispatch
        """

        if not has_access(request):
            raise PermissionDenied

        return super(DashboardMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Sets context data on superclass, before populating it further with
        the context data needed by dashboard.
        :param kwargs: Keyword arguments
        :return: A context dictionary
        """

        context = super(DashboardMixin, self).get_context_data(**kwargs)
        context.update(get_base_context(self.request))

        return context


class DashboardPermissionMixin(DashboardMixin, PermissionRequiredMixin):
    """
    DashboardPermissionMixin combines the DashboardMixin with Django
    Guardian's permission based mixin, rendering a 403 Unauthorized
    template if the currently logged in user is lacking appropriate
    permissions to access a certain view.
    """

    def get_permission_object(self, *args, **kwargs):
        """
        By default PermissionRequiredMixin works with object permissions.
        By returning None we force guardian to only check if the user
        has the proper permission.
        """
        return None

    return_403 = True
