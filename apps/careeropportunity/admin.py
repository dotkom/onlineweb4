# -*- coding: utf-8 -*-

from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.careeropportunity.models import CareerOpportunity


class CareerOpportunityAdmin(VersionAdmin):
    model = CareerOpportunity
    list_display = ['__str__', 'company', 'employment', 'start', 'end', 'featured']
    list_filter = ['employment']
    search_fields = ['company__name']


admin.site.register(CareerOpportunity, CareerOpportunityAdmin)
