from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from guardian.decorators import permission_required

from apps.dashboard.tools import has_access


@login_required
@permission_required('resourcecenter.view_resource', return_403=True)
def index(request):

    if not has_access(request):
        raise PermissionDenied

    return render(request, 'resourcecenter/dashboard/index.html')
