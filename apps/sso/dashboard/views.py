# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/25/15

import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone

from oauth2_provider.models import Application, AccessToken

from apps.dashboard.tools import get_base_context

log = logging.getLogger('SSO')


@login_required()
def index(request):
    """
    Main viewcontroller of the Dashboard SSO module
    :param request: Django request object
    :return: An HttpResponse
    """

    if not request.user.is_superuser:
        return PermissionDenied

    context = get_base_context(request)

    context['apps'] = Application.objects.all().order_by('name')

    return render(request, 'sso/dashboard/index.html', context)
