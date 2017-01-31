from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.splash.models import SplashEvent


class SplashEventAdmin(VersionAdmin):
    pass


admin.site.register(SplashEvent, SplashEventAdmin)
