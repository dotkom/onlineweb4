from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Mail, Mailinglist


@admin.register(Mailinglist)
class MailinglistAdmin(VersionAdmin):
    filter_horizontal = ("members",)
    fields = ("email_name", "name", "description", "public", "members")


@admin.register(Mail)
class OrganizaitonMailAdmin(VersionAdmin):
    fields = ("email", "name", "description", "public")
