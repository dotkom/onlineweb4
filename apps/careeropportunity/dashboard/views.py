# -*- encoding: utf-8 -*-
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from guardian.decorators import permission_required

from apps.careeropportunity.forms import AddCareerOpportunityForm
from apps.careeropportunity.models import CareerOpportunity
from apps.dashboard.tools import get_base_context, has_access


@login_required
@permission_required('careeropportunity.show_careeropportunity', return_403=True)
def index(request):

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    # "cops" is short for "careeropportunities" which is a fucking long word
    # "cop" is short for "careeropportunity" which also is a fucking long word
    cops = CareerOpportunity.objects.all()
    context['cops'] = cops.filter(end__gte=timezone.now()).order_by('end')
    context['archive'] = cops.filter(end__lte=timezone.now()).order_by('-id')
    context['all'] = cops
    return render(request, 'careeropportunity/dashboard/index.html', context)


@login_required
@permission_required('careeropportunity.change_careeropportunity', return_403=True)
def detail(request, opportunity_id=None):
    logger = logging.getLogger(__name__)
    logger.debug('Editing careeropportunity with id: %s' % (opportunity_id))

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)
    cop = None
    if opportunity_id:
        cop = get_object_or_404(CareerOpportunity, pk=opportunity_id)
        context['cop'] = cop
        context['form'] = AddCareerOpportunityForm(instance=cop)
    else:
        context['form'] = AddCareerOpportunityForm()

    if request.method == 'POST':
        if cop:
            form = AddCareerOpportunityForm(data=request.POST, instance=cop)
        else:
            form = AddCareerOpportunityForm(data=request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'La til ny karrieremulighet')
            return redirect(index)
        else:
            context['form'] = form
            messages.error(request,
                           'Skjemaet ble ikke korrekt utfylt. Se etter markerte felter for å se hva som gikk galt.')

    return render(request, 'careeropportunity/dashboard/detail.html', context)


@login_required
@permission_required('careeropportunity.change_careeropportunity', return_403=True)
def delete(request, opportunity_id=None):
    logger = logging.getLogger(__name__)
    logger.debug('Deleting careeropportunitywith id: %s' % (opportunity_id))
    if not has_access(request):
        raise PermissionDenied

    cop = get_object_or_404(CareerOpportunity, pk=opportunity_id)
    cop.delete()
    messages.success(request, 'Slettet karrieremuligheten')
    return redirect(index)
