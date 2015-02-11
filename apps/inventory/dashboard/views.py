# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404

from guardian.decorators import permission_required

from apps.dashboard.tools import has_access, get_base_context
from apps.inventory.models import Item, Batch


@login_required
@permission_required('inventory.view_item', return_403=True)
def index(request):

    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context['items'] = Item.objects.all().order_by('name')

    return render(request, 'inventory/dashboard/index.html', context)


@login_required
@permission_required('inventory.change_item', return_403=True)
def details(request, pk):
    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context['item'] = get_object_or_404(Item, pk=pk)

    return render(request, 'inventory/dashboard/details.html', context)
