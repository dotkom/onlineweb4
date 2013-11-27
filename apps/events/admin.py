# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
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
from apps.feedback.admin import FeedbackRelationInline



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


class AttendeeAdmin(admin.ModelAdmin):
    model = Attendee
    list_display = ('user', 'event')


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

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['ingress_short'].validators=[validators.MinLengthValidator(50)]
        form.base_fields['ingress'].validators=[validators.MinLengthValidator(75)]
        form.base_fields['description'].validators=[
                                                    validators.MinLengthValidator(140),
                                                    ]
        return form

admin.site.register(Event, EventAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(AttendanceEvent, AttendanceEventAdmin)
admin.site.register(RuleBundle, RuleBundleAdmin)
admin.site.register(GradeRule, GradeRuleAdmin)
admin.site.register(UserGroupRule, UserGroupRuleAdmin)
admin.site.register(FieldOfStudyRule, FieldOfStudyRuleAdmin)
