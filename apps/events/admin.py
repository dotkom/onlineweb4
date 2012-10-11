# -*- coding: utf-8 -*-

from apps.events.models import Event, AttendanceEvent, Attendee
from django.contrib import admin

class AttendanceEventInline(admin.StackedInline):
    model = AttendanceEvent
    max_num = 1
    extra = 0

# class AttendeeInline(admin.StackedInline):
#     model = Attendee
#     extra = 0

class EventAdmin(admin.ModelAdmin):
    inlines = ( AttendanceEventInline,
                # AttendeeInline)
                )
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()

admin.site.register(Event, EventAdmin)
