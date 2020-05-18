# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets

from .filters import CompanyFilter
from .models import Company
from .serializers import CompanySerializer


def details(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    return render(request, "company/details.html", {"company": company})


class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    filterset_class = CompanyFilter
