# -*- coding: utf-8 -*-

from apps.feedback.models import Feedback
from apps.feedback.models import FieldOfStudy
from apps.feedback.models import Text

from django.contrib import admin


class FieldOfStudyInline(admin.StackedInline):
    model = FieldOfStudy

class TextInline(admin.StackedInline):
    model = Text
    extra = 0

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('description', 'author')
    inlines = (FieldOfStudyInline, TextInline)
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if not change:  # created
            obj.author = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()

admin.site.register(Feedback, FeedbackAdmin)
