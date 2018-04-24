from django.contrib import admin

from apps.resourcecenter.models import Resource


class ResourceCenterAdmin(admin.ModelAdmin):
    model = Resource
    list_display = ['title', 'priority']


admin.site.register(Resource, ResourceCenterAdmin)
