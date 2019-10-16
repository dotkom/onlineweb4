from django.contrib import admin
from django.utils.translation import ugettext as _
from reversion.admin import VersionAdmin

from apps.posters.models import Poster


class PosterAdmin(VersionAdmin):
    model = Poster
    list_display = (
        "event",
        "title",
        "assigned_to",
        "display_from",
        "ordered_date",
        "ordered_by",
        "ordered_committee",
    )
    fieldsets = (
        (
            _("Event info"),
            {"fields": ("event", "title", "price", "description", "comments")},
        ),
        (_("Order info"), {"fields": ("amount",)}),
        (
            _("proKom"),
            {
                "fields": (
                    "display_from",
                    "assigned_to",
                    "ordered_by",
                    "ordered_committee",
                    "finished",
                )
            },
        ),
    )
    search_fields = ("title", "category", "company", "when")


admin.site.register(Poster, PosterAdmin)
# username, expiration_date, registered, note
