# -*- encoding: utf-8 -*-

import json

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from apps.dashboard.tools import has_access, get_base_context
from apps.marks.models import Mark, MarkUser
from apps.authentication.models import OnlineUser as User

@login_required
@permission_required('marks.can_view', return_403=True)
def index(request):
    """
    Marks overview
    """

    # Check access
    if not has_access(request):
        raise PermissionDenied

    # Get context
    context = get_base_context(request)

    # Find all marks and do additional fixes
    marks_collection = []
    marks = list(Mark.objects.all())
    for mark in marks:
        marks_temp = mark
        marks_temp.users_num = len(mark.given_to.all())
        marks_temp.category_clean = mark.get_category_display()

        marks_collection.append(marks_temp)

    # Add collection to context
    context['marks'] = marks_collection

    # Render view
    return render(request, 'marks/dashboard/index.html', context)

@login_required
@permission_required('marks.can_add', return_403=True)
def marks_details(request, pk):
    """
    Display details for a given Mark
    """

    # Check permission
    if not has_access(request):
        raise PermissionDenied

    # Get context
    context = get_base_context(request)

    # Get object
    mark = get_object_or_404(Mark, pk=pk)
    mark.category_clean = mark.get_category_display()
    context['mark'] = mark

    # Get users connected to the mark
    context['mark_users'] = mark.given_to.all()

    # AJAX
    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST:
            resp = {'status': 200}
            if request.POST['action'] == 'remove_user':
                # Get the correct user
                user = get_object_or_404(User, pk=int(request.POST['user_id']))

                # Remove from the set
                mark_users_filtered = []
                for mark_user in context['mark_users']:
                    if mark_user.user == user:
                        # Delete the object in the database
                        mark_user.delete()
                    else:
                        mark_users_filtered.append(mark_user)

                # Set information to resp
                resp['message'] = '%s ble fjernet fra %s' % (user.get_full_name(), context['mark'].title)
                resp['mark_users'] = [{'user': mu.user.get_full_name(), 'id': mu.user.id} for mu in mark_users_filtered]

                # Return ajax
                return HttpResponse(json.dumps(resp), status=200)
            elif request.POST['action'] == 'add_user':
                user = get_object_or_404(User, pk=int(request.POST['user_id']))

                # Check if user already is the lucky owner of this prikk
                for context_mark_user in context['mark_users']:
                    if context_mark_user.user == user:
                        resp = {'status': 500}
                        resp['message'] = '%s har allerede prikken %s.' % (user.get_full_name(), context['mark'].title)

                        # Return ajax
                        return HttpResponse(json.dumps(resp), status=500)

                # New MarkUser
                mark_user = MarkUser()
                mark_user.mark = context['mark']
                mark_user.user = user
                mark_user.save()

                # Build new list of users
                mark_users_list = []
                for context_mark_user in context['mark_users']:
                    mark_users_list.append(context_mark_user)
                mark_users_list.append(mark_user)

                # Sort the list of mark users
                resp['mark_users'] = [{'user': mu.user.get_full_name(), 'id': mu.user.id} for mu in mark_users_list]
                resp['mark_users'].sort(key=lambda x: x['user'])

                # Set information to resp
                resp['message'] = '%s ble tildelt prikken %s.' % (user.get_full_name(), context['mark'].title)

                # Return ajax
                return HttpResponse(json.dumps(resp), status=200)

    # Render view
    return render(request, 'marks/dashboard/marks_details.html', context)

@login_required
@permission_required('marks.can_add', return_403=True)
def marks_new(request):
    """
    Here
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'marks/dashboard/marks_new.html', context)
