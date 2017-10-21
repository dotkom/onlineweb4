# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.utils import timezone
# API v1
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.careeropportunity.models import CareerOpportunity
from apps.careeropportunity.serializers import CareerSerializer
# from apps.companyprofile.models import Company


def index(request):
    return render(request, 'careeropportunity/index.html')

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
