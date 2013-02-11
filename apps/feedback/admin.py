# -*- coding: utf-8 -*-

from apps.feedback.models import Feedback
from apps.feedback.models import FeedbackRelation
from apps.feedback.models import FieldOfStudyQuestion
from apps.feedback.models import FieldOfStudyAnswer
from apps.feedback.models import TextQuestion
from apps.feedback.models import TextAnswer
from apps.feedback.models import RatingQuestion
from apps.feedback.models import RatingAnswer


from django.forms.models import ModelForm
from django.contrib import admin
from django.contrib.contenttypes import generic


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """
        Should return True if data differs from initial.
        By always returning true even unchanged inlines will get
        validated and saved.
        """
        return True


class FeedbackRelationInline(generic.GenericStackedInline):
    model = FeedbackRelation
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    exclude = ("answered", )


class FeedbackRelationAdmin(admin.ModelAdmin):
    model = FeedbackRelation
    related_lookup_fields = {
        'generic': [['content_type', 'object_id']],
    }


class FieldOfStudyInline(admin.StackedInline):
    model = FieldOfStudyQuestion
    extra = 0
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    form = AlwaysChangedModelForm


class TextInline(admin.StackedInline):
    model = TextQuestion
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    extra = 0


class RatingInline(admin.StackedInline):
    model = RatingQuestion
    classes = ('grp-collapse grp-open',)  # style
    inline_classes = ('grp-collapse grp-open',)  # style
    extra = 0


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('description', 'author')

    inlines = (FieldOfStudyInline, TextInline, RatingInline)
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if not change:  # created
            obj.author = request.user
        obj.save()


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(FeedbackRelation, FeedbackRelationAdmin)

# TODO:  The answers do not usally need to be edited in the admin
#        interface.  (Sigurd) 2013-02-02


class FieldOfStudyAnswerAdmin(admin.ModelAdmin):
    model = FieldOfStudyAnswer


class TextAnswerAdmin(admin.ModelAdmin):
    model = TextAnswer


class RatingAnswerAdmin(admin.ModelAdmin):
    model = RatingAnswer

admin.site.register(FieldOfStudyAnswer, FieldOfStudyAnswerAdmin)
admin.site.register(TextAnswer, TextAnswerAdmin)
admin.site.register(RatingAnswer, RatingAnswerAdmin)
