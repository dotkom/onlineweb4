# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _
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
    list_display = ['__str__', 'category', 'added_date']
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


@admin.register(Suspension)
class SuspensionAdmin(VersionAdmin):
    model = Suspension

    exclude = ('payment_id',)


@admin.register(MarkRuleSet)
class MarkRuleSetAdmin(VersionAdmin):
    model = MarkRuleSet
    list_display = ('__str__', 'valid_from_date', 'created_date',)
    search_fields = ('__str__', 'valid_from_date', 'created_date', 'content',)
