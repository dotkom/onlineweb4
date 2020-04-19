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


@admin.register(MailEntity)
class MailEntityAdmin(VersionAdmin):
    fields = ("email", "name", "description", "public")
