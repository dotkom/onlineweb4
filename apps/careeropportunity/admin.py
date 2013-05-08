# -*- coding: utf-8 -*-

from apps.careeropportunity.models import CareerOpportunity

from django.contrib import admin

class CareerOpportunityAdmin(admin.ModelAdmin):
    model = CareerOpportunity

admin.site.register(CareerOpportunity, CareerOpportunityAdmin)
