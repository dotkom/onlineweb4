# -*- coding: utf-8 -*-

from apps.events.models import Event
from apps.events.models import Attendee
from apps.events.models import AttendanceEvent
from django.contrib import admin


class AdminAttendanceEvent(admin.ModelAdmin):
    list_display = ('title',) 

admin.site.register(Event)
admin.site.register(AttendanceEvent, AdminAttendanceEvent)
admin.site.register(Attendee)
