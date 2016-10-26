# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import timezone
# API v1
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.careeropportunity.models import CareerOpportunity
from apps.careeropportunity.serializers import CareerSerializer


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

class CareerViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    Viewset for Career serializer
    """

    queryset = CareerOpportunity.objects.filter(
        start__lte=timezone.now(),
        end__gte=timezone.now()
    ).order_by('-featured', '-start')
    serializer_class = CareerSerializer
    permission_classes = (AllowAny,)
