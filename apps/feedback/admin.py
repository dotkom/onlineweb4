from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.forms.models import ModelForm
from reversion.admin import VersionAdmin

from apps.feedback.models import (
    Choice,
    Feedback,
    FeedbackRelation,
    GenericSurvey,
    MultipleChoiceQuestion,
    MultipleChoiceRelation,
    RatingQuestion,
    TextQuestion,
)


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """
        Should return True if data differs from initial.
        By always returning true even unchanged inlines will get
        validated and saved.
        """
        return True


class FeedbackRelationInline(GenericStackedInline):
    model = FeedbackRelation
    extra = 0
    classes = ("grp-collapse grp-open",)  # style
    inline_classes = ("grp-collapse grp-open",)  # style
    exclude = ("answered", "active", "first_mail_sent")


@admin.register(FeedbackRelation)
class FeedbackRelationAdmin(VersionAdmin):
    model = FeedbackRelation
    related_lookup_fields = {"generic": [["content_type", "object_id"]]}


class TextInline(admin.StackedInline):
    model = TextQuestion
    classes = ("grp-collapse grp-open",)  # style
    inline_classes = ("grp-collapse grp-open",)  # style
    extra = 0


class RatingInline(admin.StackedInline):
    model = RatingQuestion
    classes = ("grp-collapse grp-open",)  # style
    inline_classes = ("grp-collapse grp-open",)  # style
    extra = 0


class ChoiceInline(admin.StackedInline):
    model = Choice
    classes = ("grp-collapse grp-open",)  # style
    inline_classes = ("grp-collapse grp-open",)  # style
    extra = 0


@admin.register(MultipleChoiceQuestion)
class MultipleChoiceAdmin(VersionAdmin):
    model = MultipleChoiceRelation
    inlines = (ChoiceInline,)
    classes = ("grp-collapse grp-open",)  # style
    inline_classes = ("grp-collapse grp-open",)  # style
    extra = 0


class MultipleChoiceInline(admin.StackedInline):
    model = MultipleChoiceRelation
    classes = ("grp-collapse grp-open",)  # style
    inline_classes = ("grp-collapse grp-open",)  # style
    extra = 0


@admin.register(Feedback)
class FeedbackAdmin(VersionAdmin):
    list_display = ("description", "author", "display_field_of_study", "display_info")
    list_filter = ["display_field_of_study", "display_info"]

    inlines = (TextInline, RatingInline, MultipleChoiceInline)
    exclude = ("author",)

    def save_model(self, request, obj, form, change):
        if not change:  # created
            obj.author = request.user
        obj.save()


@admin.register(GenericSurvey)
class GenericSurveyAdmin(VersionAdmin):
    list_display = (
        "title",
        "feedback",
        "owner",
        "owner_group",
        "created_date",
        "deadline",
    )
    list_filter = (
        "title",
        "owner__first_name",
        "owner__last_name",
        "owner_group__name",
    )
    model = GenericSurvey
