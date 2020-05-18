from django.contrib import admin

from apps.hobbygroups.models import Hobby


class HobbygroupAdmin(admin.ModelAdmin):
    model = Hobby
    list_display = ["title", "priority", "active"]


admin.site.register(Hobby, HobbygroupAdmin)
