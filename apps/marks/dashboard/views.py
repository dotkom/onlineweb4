# -*- encoding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required
from apps.dashboard.tools import has_access, get_base_context
from django.shortcuts import render, get_object_or_404

from apps.marks.models import Mark

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
    context['mark'] = mark

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
