# -*- coding: utf8 -*-
#
# Created by 'myth' on 6/25/15

import logging

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect

from oauth2_provider.settings import oauth2_settings

from apps.dashboard.tools import get_base_context
from apps.sso.models import Client
from apps.sso.dashboard.forms import NewClientForm

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

    # Fetch all clients sorted by name
    context['apps'] = Client.objects.all().order_by('name')

    # Add all available scopes from settings dict (sorted)
    context['available_scopes'] = sorted((k, v) for k, v in oauth2_settings.user_settings['SCOPES'].items())

    return render(request, 'sso/dashboard/index.html', context)


@login_required()
def new_app(request):
    """
    Viewcontroller for the creation of new apps that can access user information
    :param request: Django request object
    :return: An HttpResponse
    """

    if not request.user.is_superuser:
        return PermissionDenied

    context = get_base_context(request)

    if request.method == 'POST':
        # Bind the request data to the model form
        client_form = NewClientForm(request.POST)

        if not client_form.is_valid():
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')
        else:
            # We save but not commit to get a Client instance
            client = client_form.save(commit=False)

            # Add the user that performed the request as singlehandedly responsible for all shenanigans
            # related to this application :)
            client.user = request.user

            # We definetly want to keep this off as default for now. Can change it in the regular admin
            # panel for later, as this will automatically approve the OAuth authorization request.
            # It is intended for In-house applications that are pre-approved.
            client.skip_authorization = False

            client.save()
            messages.success(request, u'App-klienten ble opprettet')
            return redirect(reverse('sso:app_details', kwargs={'app_pk': client.id}))

        context['form'] = client_form

    else:
        context['form'] = NewClientForm()

    return render(request, 'sso/dashboard/new_app.html', context)


@login_required()
def app_details(request, app_pk):
    """
    Viewcontroller for detailed view of a specific registered app
    :param request: Django request object
    :return: An HttpResponse
    """

    if not request.user.is_superuser:
        return PermissionDenied

    context = get_base_context(request)

    context['app'] = get_object_or_404(Client, pk=app_pk)

    return render(request, 'sso/dashboard/app_details.html', context)
