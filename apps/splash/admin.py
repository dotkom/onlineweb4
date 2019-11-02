from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.splash.models import AudienceGroup, SplashEvent


@admin.register(SplashEvent)
class SplashEventAdmin(VersionAdmin):
    model = SplashEvent
    ordering = ["-start_time"]
    list_display = ["title", "start_time", "end_time"]


@admin.register(AudienceGroup)
class AudienceGroupAdmin(VersionAdmin):
    model = AudienceGroup
    list_display = ("name",)
