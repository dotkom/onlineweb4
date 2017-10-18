# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from apps.careeropportunity.models import CareerOpportunity


def index(request):
    opportunities = CareerOpportunity.objects.filter(
        start__lte=timezone.now(),
        end__gte=timezone.now()
    ).order_by('-featured', '-start')

    return render(
        request,
        'careeropportunity/index.html',
        {'opportunities': opportunities},
    )


def details(request, opportunity_id):
    opportunity = get_object_or_404(CareerOpportunity, pk=opportunity_id)

    return render(
        request,
        'careeropportunity/details.html',
        {'opportunity': opportunity},
    )
