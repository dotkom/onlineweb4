# -*- coding: utf-8 -*-

from apps.feedback.models import Feedback
from apps.feedback.models import FieldOfStudy

from django.contrib import admin


class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 1

class FieldOfStudyInline(admin.TabularInline):
    model = FieldOfStudy
    extra = 1

class FeedbackAdmin(admin.ModelAdmin):
    inlines = (FeedbackInline, FieldOfStudyInline)

    def save_model(self, request, obj, form, change):
        if not change:  # created
            obj.author = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()

admin.site.register(Feedback, FeedbackAdmin)
