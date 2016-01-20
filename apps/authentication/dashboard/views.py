# -*- encoding: utf-8 -*-

import json

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.generic import UpdateView, DetailView, DeleteView, ListView

from guardian.decorators import permission_required
from watson.views import SearchView

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import AllowedUsername
from apps.authentication.forms import UserUpdateForm
from apps.dashboard.tools import has_access, get_base_context, DashboardPermissionMixin


@login_required
def index(request):
    """
    This is the main dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'auth/dashboard/index.html', context)


# GROUP MODULE VIEWS
@login_required
@permission_required('authentication.change_onlineuser', return_403=True)
def groups_index(request):
    """
    Group module in dashboard that lists groups.
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    context['groups'] = list(Group.objects.all())
    context['groups'].sort(key=lambda x: str(x).lower())

    return render(request, 'auth/dashboard/groups_index.html', context)


@login_required
@permission_required('authentication.change_onlineuser', return_403=True)
def groups_detail(request, pk):
    """
    Group module in dashboard that lists groups.
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    context['group'] = get_object_or_404(Group, pk=pk)

    # AJAX
    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST:
            resp = {'status': 200}
            if request.POST['action'] == 'remove_user':
                user = get_object_or_404(User, pk=int(request.POST['user_id']))
                context['group'].user_set.remove(user)
                resp['message'] = '%s ble fjernet fra %s' % (user.get_full_name(), context['group'].name)
                resp['users'] = [{'user': u.get_full_name(), 'id': u.id} for u in context['group'].user_set.all()]
                resp['users'].sort(key=lambda x: x['user'])

                return HttpResponse(json.dumps(resp), status=200)
            elif request.POST['action'] == 'add_user':
                user = get_object_or_404(User, pk=int(request.POST['user_id']))
                context['group'].user_set.add(user)
                resp['full_name'] = user.get_full_name()
                resp['users'] = [{'user': u.get_full_name(), 'id': u.id} for u in context['group'].user_set.all()]
                resp['users'].sort(key=lambda x: x['user'])
                resp['message'] = '%s ble lagt til i %s' % (resp['full_name'], context['group'].name)

                return HttpResponse(json.dumps(resp), status=200)

        return HttpResponse('Ugyldig handling.', status=400)

    if hasattr(settings, 'GROUP_SYNCER') and settings.GROUP_SYNCER:
        group_id = int(pk)
        # Groups that list this one as their destination
        context['sync_group_from'] = []
        # Groups that list this one as one of their sources
        context['sync_group_to'] = []

        # Make a dict that simply maps {id: name} for all groups
        groups = {g.id: g.name for g in Group.objects.all().order_by('id')}

        for job in settings.GROUP_SYNCER:
            if group_id in job['source']:
                context['sync_group_to'].extend([groups[group_id] for group_id in job['destination']])
            if group_id in job['destination']:
                context['sync_group_from'].extend([groups[group_id] for group_id in job['source']])

    context['group_users'] = list(context['group'].user_set.all())

    context['group_permissions'] = list(context['group'].permissions.all())

    context['group_users'].sort(key=lambda x: str(x).lower())
    context['group_permissions'].sort(key=lambda x: str(x))

    return render(request, 'auth/dashboard/groups_detail.html', context)


@login_required
@permission_required("authentication.view_allowedusername", return_403=True)
def members_index(request):

    """
    Index overview for allowedusernames in dashboard
    """

    if not has_access(request):
        raise PermissionDenied

    def merge_names(members):
        for i in members:
            user = list(User.objects.filter(ntnu_username=i.username))
            if user:
                i.full_name = user[0].get_full_name()
        return members

    context = get_base_context(request)
    members = AllowedUsername.objects.all()
    context['members'] = merge_names(members)

    return render(request, 'auth/dashboard/user_list.html', context)


class UserListView(DashboardPermissionMixin, ListView):
    model = User
    queryset = User.objects.all().exclude(id=-1)
    paginate_by = 25
    paginator_class = Paginator
    permission_required = 'authentication.view_onlineuser'
    template_name = 'auth/dashboard/user_list.html'


class UserSearchView(DashboardPermissionMixin, SearchView):
    model = User
    queryset = User.objects.all().exclude(id=-1)
    paginate_by = 25
    paginator_class = Paginator
    permission_required = 'authentication.view_onlineuser'
    template_name = 'auth/dashboard/user_list.html'
    empty_query_redirect = reverse_lazy('user_list')


class UserDetailView(DashboardPermissionMixin, DetailView):
    model = User
    context_object_name = 'user'
    permission_required = 'authentication.view_onlineuser'
    pk_url_kwarg = 'user_id'
    template_name = 'auth/dashboard/user_detail.html'


class UserUpdateView(DashboardPermissionMixin, UpdateView):
    form_class = UserUpdateForm
    model = User
    permission_required = 'authentication.change_onlineuser'
    pk_url_kwarg = 'user_id'
    template_name = 'auth/dashboard/user_edit.html'

    def get_success_url(self):
        return reverse('dashboard_user_detail', kwargs={'user_id': self.kwargs.get('user_id')})


class UserDeleteView(DashboardPermissionMixin, DeleteView):
    model = User
    permission_required = 'authentication.delete_onlineuser'
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('auth_index')


@login_required
@permission_required("authentication.add_allowedusername", return_403=True)
def members_new(request):
    """
    Create new allowedusername form and handling
    """
    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'auth/dashboard/members_new.html', context)
