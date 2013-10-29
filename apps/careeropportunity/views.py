#-*- coding: utf-8 -*-
from datetime import datetime

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from apps.careeropportunity.models import CareerOpportunity


def index(request):
    opportunities = CareerOpportunity.objects.filter(
    	start__lte=datetime.now(), end__gte=datetime.now()).order_by('featured', '-start')
    
    return render_to_response('careeropportunity/index.html', \
            {'featured_opportunities': featured_opportunities, 'opportunities': opportunities}, \
            context_instance=RequestContext(request))


def details(request, opportunity_id):
    opportunity = get_object_or_404(CareerOpportunity, pk=opportunity_id)

    return render_to_response('careeropportunity/details.html', \
            {'opportunity': opportunity}, \
            context_instance=RequestContext(request))