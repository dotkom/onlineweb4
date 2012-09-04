from django.contrib import admin
from models import Event
from models import EventCompanyExt
from models import EventNewsExt
from models import EventAttendanceExt
from models import EventAttendancePaymentExt


class EventCompanyExtInline(admin.StackedInline):
    model = EventCompanyExt
    max_num = 1
    extra = 0


class EventNewsExtInline(admin.StackedInline):
    model = EventNewsExt
    max_num = 1
    extra = 0


class EventAttendancePaymentExtInline(admin.StackedInline):
    model = EventAttendancePaymentExt
    max_num = 1
    extra = 0


class EventAttendanceExtInline(admin.StackedInline):
    model = EventAttendanceExt
    max_num = 1
    extra = 0

    inlines = (EventAttendancePaymentExtInline, )
    # above line does not work
    # https://code.djangoproject.com/ticket/9025


class EventAdmin(admin.ModelAdmin):
    inlines = (EventCompanyExtInline,
               EventNewsExtInline,
               EventAttendanceExtInline,)

admin.site.register(Event, EventAdmin)
