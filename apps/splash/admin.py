from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.splash.models import SplashEvent


class SplashEventAdmin(VersionAdmin):
    model = SplashEvent
    ordering = ['-start_time']
    list_display = ['title', 'start_time', 'end_time']


admin.site.register(SplashEvent, SplashEventAdmin)
