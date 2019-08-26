# -*- coding: utf-8 -*-

from django.contrib import admin, messages
from django.utils.translation import ugettext as _
from guardian.admin import GuardedModelAdmin
from reversion.admin import VersionAdmin

from apps.events.models import (AttendanceEvent, Attendee, CompanyEvent, Event, Extras,
                                FieldOfStudyRule, GradeRule, GroupRestriction, Registration,
                                Reservation, Reservee, RuleBundle, UserGroupRule)
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
    ordering = ['-timestamp']
    list_display = ('user', 'event', 'timestamp', 'paid', 'attended', 'note', 'extras')
    list_filter = ('attended', 'paid', 'event__event')
    search_fields = (
        'event__event__title', '=event__event__id', 'user__first_name', 'user__last_name', 'user__username',
    )
    actions = [mark_paid, mark_attended, mark_not_paid, mark_not_attended]
    group_owned_objects_field = 'event__event__organizer'
    user_can_access_owned_by_group_objects_only = True

    # Disable delete_selected http://bit.ly/1o4nleN
    def get_actions(self, request):
        actions = super(AttendeeAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


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


class RegistrationInlineAdmin(admin.StackedInline):
    model = Registration
    extra = 0
    filter_horizontal = ('rule_bundles',)


@admin.register(AttendanceEvent)
class AttendanceEventAdmin(admin.ModelAdmin):
    inlines = (RegistrationInlineAdmin, )
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    exclude = ("marks_has_been_set",)

    group_owned_objects_field = 'event__organizer'
    user_can_access_owned_by_group_objects_only = True


class AttendanceEventInline(admin.StackedInline):
    model = AttendanceEvent
    max_num = 1
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    exclude = ("marks_has_been_set",)


class EventAdmin(GuardedModelAdmin, VersionAdmin):
    inlines = (AttendanceEventInline, FeedbackRelationInline, CompanyInline, GroupRestrictionInline)
    exclude = ("author", )
    list_display = ['__str__', 'event_type', 'organizer']
    list_filter = ['event_type', 'organizer']
    search_fields = ('title',)

    group_owned_objects_field = 'organizer'
    user_can_access_owned_by_group_objects_only = True

    def save_model(self, request, obj, form, change):
        if not change:  # created
            obj.author = request.user
        obj.save()


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
    list_display = ('registration', '_number_of_seats_taken', 'seats', '_attendees', '_max_capacity')
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    user_can_access_owned_by_group_objects_only = True
    group_owned_objects_field = 'registration__attendance__event__organizer'

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
        registration = Registration.objects.get(pk=obj.registration_id)
        number_of_free_seats = registration.max_capacity - registration.number_of_attendees
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
