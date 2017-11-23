# -*- coding: utf-8 -*-

from django.contrib import admin, messages
from django.utils.translation import ugettext as _
from guardian.admin import GuardedModelAdmin
from reversion.admin import VersionAdmin

from apps.events.models import (AttendanceEvent, Attendee, CompanyEvent, Event, Extras,
                                FieldOfStudyRule, GradeRule, GroupRestriction, Reservation,
                                Reservee, RuleBundle, UserGroupRule)
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


class ExtrasInline(admin.TabularInline):
    model = Extras
    extra = 1
    max_num = 20
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


class GroupRestrictionInline(admin.TabularInline):
    model = GroupRestriction
    extra = 0
    max_num = 1
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    filter_horizontal = ('groups',)


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


class AttendeeAdmin(GuardedModelAdmin, VersionAdmin):
    model = Attendee
    list_display = ('user', 'event', 'paid', 'attended', 'note', 'extras')
    list_filter = ('event__event',)
    actions = [mark_paid, mark_attended, mark_not_paid, mark_not_attended]
    group_owned_objects_field = 'event__event__organizer'
    user_can_access_owned_by_group_objects_only = True

    # Disable delete_selected http://bit.ly/1o4nleN
    def get_actions(self, request):
        actions = super(AttendeeAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_model(self, request, obj):
        event = obj.event.event
        event.attendance_event.notify_waiting_list(host=request.META['HTTP_HOST'], unattended_user=obj.user)
        obj.delete()


class CompanyEventAdmin(VersionAdmin):
    model = CompanyEvent
    inlines = (CompanyInline,)


class ExtrasAdmin(VersionAdmin):
    model = Extras
    fk_name = 'choice'
    # inlines = (ExtrasInline,)


class RuleBundleAdmin(VersionAdmin):
    model = RuleBundle


class FieldOfStudyRuleAdmin(VersionAdmin):
    model = FieldOfStudyRule


class GradeRuleAdmin(VersionAdmin):
    model = GradeRule


class UserGroupRuleAdmin(VersionAdmin):
    model = UserGroupRule


class AttendanceEventInline(admin.StackedInline):
    model = AttendanceEvent
    max_num = 1
    extra = 0
    filter_horizontal = ('rule_bundles',)
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    exclude = ("marks_has_been_set",)


class EventAdmin(GuardedModelAdmin, VersionAdmin):
    inlines = (AttendanceEventInline, FeedbackRelationInline, CompanyInline, GroupRestrictionInline)
    exclude = ("author", )
    search_fields = ('title',)

    group_owned_objects_field = 'organizer'
    user_can_access_owned_by_group_objects_only = True

    def save_model(self, request, obj, form, change):
        if not change:  # created
            obj.author = request.user
        else:
            # If attendance max capacity changed we will notify users that they are now on the attend list
            old_event = Event.objects.get(id=obj.id)
            if old_event.is_attendance_event():
                old_waitlist_size = old_event.attendance_event.waitlist_qs.count()
                if old_waitlist_size > 0:
                    diff_capacity = obj.attendance_event.max_capacity - old_event.attendance_event.max_capacity
                    if diff_capacity > 0:
                        if diff_capacity > old_waitlist_size:
                            diff_capacity = old_waitlist_size
                        # Using old_event because max_capacity has already been changed in obj
                        old_event.attendance_event.notify_waiting_list(host=request.META['HTTP_HOST'],
                                                                       extra_capacity=diff_capacity)
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()


class ReserveeInline(admin.TabularInline):
    model = Reservee
    extra = 1
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style


class ReservationAdmin(GuardedModelAdmin, VersionAdmin):
    model = Reservation
    inlines = (ReserveeInline,)
    max_num = 1
    extra = 0
    list_display = ('attendance_event', '_number_of_seats_taken', 'seats', '_attendees', '_max_capacity')
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    user_can_access_owned_by_group_objects_only = True
    group_owned_objects_field = 'attendance_event__event__organizer'

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
        attendance_event = AttendanceEvent.objects.get(pk=obj.attendance_event.event)
        number_of_free_seats = attendance_event.max_capacity - attendance_event.number_of_attendees
        if number_of_free_seats < obj.seats:
            obj.seats = number_of_free_seats
            self.message_user(request, _(
                "Du har valgt et antall reserverte plasser som overskrider antallet ledige plasser for dette "
                "arrangementet. Antallet ble automatisk justert til %d (alle ledige plasser)."
            ) % number_of_free_seats, messages.WARNING)
        obj.save()


admin.site.register(Event, EventAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(RuleBundle, RuleBundleAdmin)
admin.site.register(Extras, ExtrasAdmin)
admin.site.register(GradeRule, GradeRuleAdmin)
admin.site.register(UserGroupRule, UserGroupRuleAdmin)
admin.site.register(FieldOfStudyRule, FieldOfStudyRuleAdmin)
admin.site.register(Reservation, ReservationAdmin)
