# -*- encoding: utf-8 -*-

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from oauth2_provider.views.base import AuthorizationView as DefaultAuthorizationView, RevokeTokenView, TokenView  # flake8: noqa

_log = logging.getLogger('SSO')


@login_required
def index(request):
    """
    This is the main SSO view
    """

    context = {}

    return render(request, 'sso/index.html', context)


class AuthorizationView(DefaultAuthorizationView):
    template_name = 'sso/authorize.html'
