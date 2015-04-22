from django.contrib import admin

from apps.splash.models import SplashYear, SplashEvent


class SplashYearAdmin(admin.ModelAdmin):
	list_display = ('title', 'start_date',)

class SplashEventAdmin(admin.ModelAdmin):
	exclude = ('',)


admin.site.register(SplashYear, SplashYearAdmin)
admin.site.register(SplashEvent, SplashEventAdmin)