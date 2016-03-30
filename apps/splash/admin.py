from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.splash.models import SplashEvent, SplashYear


class SplashYearAdmin(VersionAdmin):
    list_display = ('title', 'start_date',)


class SplashEventAdmin(VersionAdmin):
    exclude = ('',)


admin.site.register(SplashYear, SplashYearAdmin)
admin.site.register(SplashEvent, SplashEventAdmin)
