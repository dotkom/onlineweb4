from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext as _
from reversion.admin import VersionAdmin

from apps.authentication.models import Membership, OnlineUser
from apps.marks.models import Mark, MarkRuleSet, MarkUser, Suspension


class MarkUserInline(admin.TabularInline):
    model = MarkUser
    extra = 1
    verbose_name = _("mottaker")
    verbose_name_plural = _("mottakere")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            # filter out only active members, and order correctly
            all_members = Membership.objects.filter(
                expiration_date__gte=timezone.now()
            ).values_list("username")

            kwargs["queryset"] = OnlineUser.objects.filter(
                ntnu_username__in=all_members
            ).order_by("first_name", "last_name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Mark)
class MarkAdmin(VersionAdmin):
    inlines = (MarkUserInline,)
    fields = [
        "title",
        "added_date",
        "cause",
        "weight",
        "description",
        "expiration_date",
        "ruleset",
    ]

    list_display = ["__str__", "category", "cause", "added_date", "weight"]
    readonly_fields = (
        "expiration_date",
        "ruleset",
    )
    search_fields = ("title",)

    def save_model(self, request, obj, form, change):
        obj.last_changed_by = request.user
        obj.save()


@admin.register(Suspension)
class SuspensionAdmin(VersionAdmin):
    model = Suspension
    list_display = ["title", "user", "created_time", "expiration_date", "cause"]

    exclude = ("payment_id",)


@admin.register(MarkRuleSet)
class MarkRuleSetAdmin(VersionAdmin):
    model = MarkRuleSet
    list_display = ("__str__", "valid_from_date", "created_date")
    search_fields = ("__str__", "valid_from_date", "created_date", "content")
