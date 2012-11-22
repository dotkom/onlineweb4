# -*- coding: utf-8 -*-

from apps.feedback.models import Feedback
from apps.feedback.models import FeedbackRelation
from apps.feedback.models import FieldOfStudyQuestion
from apps.feedback.models import FieldOfStudyAnswer
from apps.feedback.models import TextQuestion
from apps.feedback.models import TextAnswer

from django.contrib import admin


class FeedbackRelationAdmin(admin.ModelAdmin):
    model = FeedbackRelation


class FieldOfStudyInline(admin.StackedInline):
    model = FieldOfStudyQuestion
    exclude = ('field_of_study',)
    max_num = 1


class TextInline(admin.StackedInline):
    model = TextQuestion
    classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)
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


class FieldOfStudyAnswerAdmin(admin.ModelAdmin):
    model = FieldOfStudyAnswer


class TextAnswerAdmin(admin.ModelAdmin):
    model = TextAnswer


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(FieldOfStudyAnswer, FieldOfStudyAnswerAdmin)
admin.site.register(FeedbackRelation, FeedbackRelationAdmin)
admin.site.register(TextAnswer, TextAnswerAdmin)
