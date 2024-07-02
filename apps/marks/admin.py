from django.contrib import admin
from django.utils.translation import gettext as _
from reversion.admin import VersionAdmin

from apps.marks.models import Mark, MarkRuleSet, MarkUser, Suspension


class MarkUserInline(admin.TabularInline):
    model = MarkUser
    extra = 1
    verbose_name = _("mottaker")
    verbose_name_plural = _("mottakere")


@admin.register(Mark)
class MarkAdmin(VersionAdmin):
    inlines = (MarkUserInline,)
    list_display = ["__str__", "category", "added_date", "weight"]
    search_fields = ("title",)

    def save_model(self, request, obj, form, change):
        obj.last_changed_by = request.user
        obj.save()


@admin.register(Suspension)
class SuspensionAdmin(VersionAdmin):
    model = Suspension

    exclude = ("payment_id",)


@admin.register(MarkRuleSet)
class MarkRuleSetAdmin(VersionAdmin):
    model = MarkRuleSet
    list_display = ("__str__", "valid_from_date", "created_date")
    search_fields = ("__str__", "valid_from_date", "created_date", "content")
