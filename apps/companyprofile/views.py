# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets

from apps.companyprofile.models import Company
from apps.companyprofile.serializers import CompanySerializer


def details(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    return render(request, "company/details.html", {"company": company})


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    filterset_fields = ("name",)
