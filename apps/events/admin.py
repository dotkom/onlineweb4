# -*- coding: utf-8 -*-

from apps.events.models import Event
from apps.events.models import Attendee
from apps.events.models import AttendanceEvent
from django.contrib import admin

admin.site.register(Event)
admin.site.register(AttendanceEvent)
admin.site.register(Attendee)
