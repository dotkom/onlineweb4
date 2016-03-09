# -*- coding: utf-8 -*-
from apps.careeropportunity.models import Company
from django.shortcuts import get_object_or_404, render


def details(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    return render(request, 'company/details.html', {'company': company})
