# -*- encoding: utf-8 -*-

import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from oauth2_provider.views.base import AuthorizationView as DefaultAuthorizationView

# noinspection PyUnresolvedReferences
from oauth2_provider.views.base import RevokeTokenView, TokenView  # noqa: F401  # isort:skip

_log = logging.getLogger('SSO')


@login_required
def index(request):
    """
    This is the main SSO view
    """

    context = {}

    return render(request, 'sso/authorize.html', context)


class AuthorizationView(DefaultAuthorizationView):
    template_name = 'sso/authorize.html'
