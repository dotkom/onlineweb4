from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from guardian.decorators import permission_required

from apps.dashboard.tools import get_base_context, has_access


@login_required
@permission_required('hobbygroups.change_hobby', return_403=True)
def index(request):

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'hobbygroups/dashboard/index.html', context)
