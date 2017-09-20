# -*- coding: utf-8 -*-

from django.shortcuts import render
from apps.resourcecenter.models import Resource

from apps.resourcecenter.serializers import ResourceSerializer
from rest_framework import viewsets

# Index page
def index(request):
    resources = Resource.objects.all().order_by('-priority')
    context = {
        'resources': resources,
    }
    return render(request, 'resourcecenter/index.html', context)


class HobbyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
