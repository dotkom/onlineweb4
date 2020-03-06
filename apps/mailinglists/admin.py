from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Mailinglist


@admin.register(Mailinglist)
class MailinglistAdmin(VersionAdmin):
    filter_horizontal = ("contained_emails",)
    fields = ("email", "name", "description", "public", "contained_emails")
