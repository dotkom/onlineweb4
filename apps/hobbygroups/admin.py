from django.contrib import admin

from apps.hobbygroups.models import Hobby


class HobbygroupAdmin(admin.ModelAdmin):
    model = Hobby
    list_display = ['title', 'priority']


admin.site.register(Hobby)
