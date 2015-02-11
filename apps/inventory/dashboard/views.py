# -*- encoding: utf-8 -*-

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.utils.translation import ugettext as _

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

    context['items'] = Item.objects.all()

    return render(request, 'inventory/dashboard/index.html', context)
