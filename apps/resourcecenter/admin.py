from django.contrib import admin

from apps.resourcecenter.models import Resource


class ResourceCenterAdmin(admin.ModelAdmin):
    model = Resource


admin.site.register(Resource)
