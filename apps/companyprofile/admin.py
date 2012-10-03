# -*- coding: utf-8 -*-

from django.contrib import admin
from models import Company

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_description','long_description', 'site', 'email_address', 'phone_number',)

admin.site.register(Company, CompanyAdmin)
    
