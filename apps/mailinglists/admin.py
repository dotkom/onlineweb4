from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Organization, MailGroup


@admin.register(MailGroup)
class MailinglistAdmin(VersionAdmin):
    filter_horizontal = ("members",)
    fields = ("email_name", "name", "description", "public", "members")


@admin.register(Organization)
class OrganizaitonMailAdmin(VersionAdmin):
    fields = ("email", "name", "description", "public")
