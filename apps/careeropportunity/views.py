# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import timezone

from apps.careeropportunity.models import CareerOpportunity


def index(request):
    opportunities = CareerOpportunity.objects.filter(
        start__lte=timezone.now(),
        end__gte=timezone.now()
    ).order_by('-featured', '-start')

    return render_to_response(
        'careeropportunity/index.html',
        {'opportunities': opportunities},
        context_instance=RequestContext(request)
    )


def details(request, opportunity_id):
    opportunity = get_object_or_404(CareerOpportunity, pk=opportunity_id)

    return render_to_response(
        'careeropportunity/details.html',
        {'opportunity': opportunity},
        context_instance=RequestContext(request)
    )
