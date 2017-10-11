from django.contrib import admin

from apps.hobbygroups.models import Hobby


class HobbygroupAdmin(admin.ModelAdmin):
    model = Hobby


admin.site.register(Hobby)
