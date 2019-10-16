# -*- coding: utf-8 -*-

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Company


class CompanyAdmin(VersionAdmin):
    list_display = ('name', 'site', 'email_address', 'phone_number',)
    search_fields = ('name',)


admin.site.register(Company, CompanyAdmin)
