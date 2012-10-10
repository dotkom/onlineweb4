# -*- coding: utf-8 -*-

from apps.events.models import Event, AttendanceEvent, Attendee
from django.contrib import admin


admin.site.register(Event)
admin.site.register(AttendanceEvent)
admin.site.register(Attendee)
