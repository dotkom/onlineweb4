# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    """
    This is the main SSO view
    """

    context = {}

    return render(request, 'sso/index.html', context)
