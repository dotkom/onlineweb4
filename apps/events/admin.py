# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin, messages
from django.core import validators
from django.utils.translation import ugettext as _

from apps.events.models import Event
from apps.events.models import AttendanceEvent
from apps.events.models import Attendee
from apps.events.models import CompanyEvent
from apps.events.models import RuleBundle
from apps.events.models import FieldOfStudyRule
from apps.events.models import GradeRule
from apps.events.models import UserGroupRule
from apps.events.models import Reservation
from apps.events.models import Reservee
from apps.feedback.admin import FeedbackRelationInline



class AttendeeInline(admin.TabularInline):
    model = Attendee
    extra = 1
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


class CompanyInline(admin.TabularInline):
    model = CompanyEvent
    max_num = 20
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


class RuleBundleInline(admin.TabularInline):
    model = RuleBundle
    extra = 1
    max_num = 20
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


def mark_paid(modeladmin, request, queryset):
    queryset.update(paid=True)
mark_paid.short_description = "Merk som betalt"

def mark_not_paid(modeladmin, request, queryset):
    queryset.update(paid=False)
mark_not_paid.short_description = "Merk som ikke betalt"

def mark_attended(modeladmin, request, queryset):
    queryset.update(attended=True)
mark_attended.short_description = "Merk som møtt"

def mark_not_attended(modeladmin, request, queryset):
    queryset.update(attended=False)
mark_not_attended.short_description = "Merk som ikke møtt"

class AttendeeAdmin(admin.ModelAdmin):
    model = Attendee
    list_display = ('user', 'event', 'paid', 'attended', 'note')
    list_filter = ('event__event__title',)
    actions = [mark_paid, mark_attended, mark_not_paid, mark_not_attended]

    # Disable delete_selected http://bit.ly/1o4nleN
    def get_actions(self, request):
        actions = super(AttendeeAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_model(self, request, obj):
        event = obj.event.event
        event.notify_waiting_list(host=request.META['HTTP_HOST'], unattended_user=obj.user)
        obj.delete()


class CompanyEventAdmin(admin.ModelAdmin):
    model = CompanyEvent
    inlines = (CompanyInline,)


class RuleBundleAdmin(admin.ModelAdmin):
    model = RuleBundle


class FieldOfStudyRuleAdmin(admin.ModelAdmin):
    model = FieldOfStudyRule


class GradeRuleAdmin(admin.ModelAdmin):
    model = GradeRule


class UserGroupRuleAdmin(admin.ModelAdmin):
    model = UserGroupRule


class AttendanceEventInline(admin.StackedInline):
    model = AttendanceEvent
    max_num = 1
    extra = 0
    filter_horizontal = ('rule_bundles',)
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


class EventAdmin(admin.ModelAdmin):
    inlines = (AttendanceEventInline, FeedbackRelationInline, CompanyInline)
    exclude = ("author", )
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        if not change:  # created
            obj.author = request.user
        else:
            # If attendance max capacity changed we will notify users that they are now on the attend list
            old_event = Event.objects.get(id=obj.id)
            if old_event.is_attendance_event() and old_event.wait_list:
                diff_capacity = obj.attendance_event.max_capacity - old_event.attendance_event.max_capacity
                if diff_capacity > 0:
                    if diff_capacity > len(old_event.wait_list):
                        diff_capacity = len(old_event.wait_list)
                    # Using old_event because max_capacity has already been changed in obj
                    old_event.notify_waiting_list(host=request.META['HTTP_HOST'], extra_capacity=diff_capacity)
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['ingress_short'].validators=[validators.MinLengthValidator(50)]
        form.base_fields['ingress'].validators=[validators.MinLengthValidator(75)]
        form.base_fields['description'].validators=[validators.MinLengthValidator(140)]
        return form


class ReserveeInline(admin.TabularInline):
    model = Reservee
    extra = 1
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


class ReservationAdmin(admin.ModelAdmin):
    model = Reservation
    inlines = (ReserveeInline,)
    max_num = 1
    extra = 0
    list_display = ('attendance_event', '_number_of_seats_taken', 'seats', '_attendees', '_max_capacity')
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style

    def _number_of_seats_taken(self, obj):
        return obj.number_of_seats_taken
    _number_of_seats_taken.short_description = _("Fylte reservasjoner")

    def _attendees(self, obj):
        return obj.attendance_event.number_of_attendees
    _attendees.short_description = _("Antall deltakere")

    def _max_capacity(self, obj):
        return obj.attendance_event.max_capacity 
    _max_capacity.short_description = _("Arrangementets maks-kapasitet")

    def save_model(self, request, obj, form, change):
        if change:
            number_of_free_seats = obj.attendance_event.max_capacity - obj.attendance_event.number_of_attendees
            if number_of_free_seats < obj.seats:
                obj.seats = number_of_free_seats
                self.message_user(request, _("Du har valgt et antall reserverte plasser som overskrider antallet ledige plasser for dette arrangementet. Antallet ble automatisk justert til %d (alle ledige plasser).") % number_of_free_seats, messages.WARNING)
        obj.save()
            
    
admin.site.register(Event, EventAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(RuleBundle, RuleBundleAdmin)
admin.site.register(GradeRule, GradeRuleAdmin)
admin.site.register(UserGroupRule, UserGroupRuleAdmin)
admin.site.register(FieldOfStudyRule, FieldOfStudyRuleAdmin)
admin.site.register(Reservation, ReservationAdmin)
