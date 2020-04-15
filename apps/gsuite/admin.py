from django.contrib import admin

from apps.gsuite.models import ServiceAccount


class ServiceAccountAdmin(admin.ModelAdmin):
    model = ServiceAccount
    
admin.site.register(ServiceAccount, ServiceAccountAdmin)
