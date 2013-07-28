# -*- coding: utf-8 -*-

from apps.events.models import Event
from apps.events.models import AttendanceEvent
from apps.events.models import Attendee
from apps.events.models import CompanyEvent
from apps.events.models import RuleBundle
from apps.events.models import FieldOfStudyRule
from apps.events.models import GradeRule
from apps.events.models import RuleOffset
from apps.events.models import UserGroupRule

from apps.feedback.admin import FeedbackRelationInline

from django.contrib import admin


class AttendeeInline(admin.TabularInline):
    model = Attendee
    extra = 1


class CompanyInline(admin.TabularInline):
    model = CompanyEvent
    max_num = 20
    extra = 0

class RuleBundleInline(admin.TabularInline):
    model = RuleBundle
    extra = 1
    max_num = 20


class AttendanceEventAdmin(admin.ModelAdmin):
    model = AttendanceEvent
    inlines = (AttendeeInline, RuleBundleInline)

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

class RuleOffsetAdmin(admin.ModelAdmin):
    model = RuleOffset

class AttendanceEventInline(admin.StackedInline):
    model = AttendanceEvent
    max_num = 1
    extra = 0


class EventAdmin(admin.ModelAdmin):
    inlines = (AttendanceEventInline, FeedbackRelationInline, CompanyInline)
    exclude = ("author", )

    def save_model(self, request, obj, form, change):
        if not change:  # created
            obj.author = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()

admin.site.register(Event, EventAdmin)
admin.site.register(AttendanceEvent, AttendanceEventAdmin)
admin.site.register(RuleBundle, RuleBundleAdmin)
admin.site.register(GradeRule, GradeRuleAdmin)
admin.site.register(UserGroupRule, UserGroupRuleAdmin)
admin.site.register(FieldOfStudyRule, FieldOfStudyRuleAdmin)
admin.site.register(RuleOffset, RuleOffsetAdmin)
