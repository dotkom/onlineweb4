# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _
from reversion.admin import VersionAdmin

from apps.marks.models import Mark, MarkUser, Suspension


class MarkUserInline(admin.TabularInline):
    model = MarkUser
    extra = 1
    verbose_name = _("mottaker")
    verbose_name_plural = _("mottakere")


class MarkAdmin(VersionAdmin):
    inlines = (MarkUserInline,)
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.given_by = request.user
            if not obj.description:
                descriptions = {
                    0: _("Ingen begrunnelse. Kontakt %s for mer informasjon.") % obj.given_by.email,
                    1: _("Du har fått en prikk for et sosialt arrangement."),
                    2: _("Du har fått en prikk for en bedriftspresentasjon."),
                    3: _("Du har fått en prikk for et kurs."),
                    4: _("Du har fått en prikk fordi du ikke har levert tilbakemelding."),
                    5: _("Du har fått en prikk relatert til kontoret."),
                }
                obj.description = descriptions[obj.category]

        obj.last_changed_by = request.user
        obj.save()


class SuspensionAdmin(VersionAdmin):
    model = Suspension

    exclude = ('payment_id',)


admin.site.register(Mark, MarkAdmin)
admin.site.register(Suspension, SuspensionAdmin)
