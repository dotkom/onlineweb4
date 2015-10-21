# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from apps.careeropportunity.models import Company


def details(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    return render(request, 'company/details.html', {'company': company})
