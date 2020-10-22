from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import MailEntity, MailGroup


@admin.register(MailGroup)
class MailGroupAdmin(VersionAdmin):
    readonly_fields = ("email",)
    filter_horizontal = ("members",)
    fields = (
        "email_local_part",
        "domain",
        "name",
        "email",
        "description",
        "public",
        "members",
    )

    def get_exclude(self, request, obj=None):
        # Hide email-field on create-form, since it's not relevant
        # until the generated e-mail can be made
        return ("email",) if obj is None else None


@admin.register(MailEntity)
class MailEntityAdmin(VersionAdmin):
    fields = ("email", "name", "description", "public")
