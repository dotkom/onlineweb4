# -*- coding: utf-8 -*-

from apps.feedback.models import Feedback
from apps.feedback.models import FieldOfStudyQuestion
from apps.feedback.models import TextQuestion
from apps.feedback.models import Answer
from apps.feedback.models import FeedbackToObjectRelation
from django.contrib import admin


class FeedbackToObjectRelationAdmin(admin.ModelAdmin):
    model = FeedbackToObjectRelation


class FieldOfStudyInline(admin.StackedInline):
    model = FieldOfStudyQuestion


class TextInline(admin.StackedInline):
    model = TextQuestion
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


class AnswerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(FeedbackToObjectRelation, FeedbackToObjectRelationAdmin)
