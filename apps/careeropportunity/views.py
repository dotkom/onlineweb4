# -*- coding: utf-8 -*-

from django.db.models import Q
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import timezone

from apps.companyprofile.models import Company
from apps.careeropportunity.models import CareerOpportunity


def index(request):
    opportunities = CareerOpportunity.objects.filter(
        start__lte=timezone.now(),
        end__gte=timezone.now()
    ).order_by('-featured', '-start')

    # Subquery to filter out only the companies that have a careeropportunity
    # visible right now, to avoid listing companies that are irrelevant
    distinct_company_opportunities = CareerOpportunity.objects.filter(
        start__lte=timezone.now(),
        end__gte=timezone.now()
    ).values_list('company', flat=True)
    companies = Company.objects.filter(
        id__in=set(distinct_company_opportunities)
    )

    employments = []
    locations = []

    for opportunity in opportunities:
        employment_slugs = opportunity.employment.slugs()
        employment_tags = opportunity.employment.all()
        for i in range(len(employment_slugs)):
            if employment_tags[i] not in employments:
                employments.append({
                    'text': employment_tags[i],
                    'slug': employment_slugs[i],
                })

        location_slugs = opportunity.location.slugs()
        location_tags = opportunity.location.all()
        for i in range(len(location_slugs)):
            if location_tags[i] not in locations:
                locations.append({
                    'text': location_tags[i],
                    'slug': location_slugs[i],
                })

    return render_to_response(
        'careeropportunity/index.html',
        {
            'opportunities': opportunities,
            'companies': companies,
            'employment_tags': employments,
            'location_tags': locations
        },
        context_instance=RequestContext(request)
    )


def details(request, opportunity_id):
    opportunity = get_object_or_404(CareerOpportunity, pk=opportunity_id)

    return render_to_response(
        'careeropportunity/details.html',
        {'opportunity': opportunity},
        context_instance=RequestContext(request)
    )
