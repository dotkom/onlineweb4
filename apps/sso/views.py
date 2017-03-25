# -*- encoding: utf-8 -*-

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

_log = logging.getLogger('SSO')


@login_required
def index(request):
    """
    This is the main SSO view
    """

    context = {}

    return render(request, 'sso/index.html', context)
