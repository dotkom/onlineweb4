# -*- coding: utf-8 -*-

from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.careeropportunity.models import CareerOpportunity


class CareerOpportunityAdmin(VersionAdmin):
    model = CareerOpportunity


admin.site.register(CareerOpportunity, CareerOpportunityAdmin)
