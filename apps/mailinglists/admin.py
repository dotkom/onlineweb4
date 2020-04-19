from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import MailGroup, MailEntity


@admin.register(MailGroup)
class MailGroupAdmin(VersionAdmin):
    filter_horizontal = ("members",)
    fields = ("email_name", "name", "description", "public", "members")


@admin.register(MailEntity)
class MailEntityAdmin(VersionAdmin):
    fields = ("email", "name", "description", "public")
