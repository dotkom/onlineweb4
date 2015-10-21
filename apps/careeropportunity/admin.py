# -*- coding: utf-8 -*-

from apps.careeropportunity.models import CareerOpportunity

from django.contrib import admin

from reversion.admin import VersionAdmin

class CareerOpportunityAdmin(VersionAdmin):
    model = CareerOpportunity

admin.site.register(CareerOpportunity, CareerOpportunityAdmin)
