#-*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.marks.models import Mark, UserEntry

class UserEntryInline(admin.TabularInline):
    model = UserEntry
    extra = 1
    verbose_name = _(u"mottaker")
    verbose_name_plural = _(u"mottakere")

class MarkAdmin(admin.ModelAdmin):
    inlines = (UserEntryInline,)
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.given_by = request.user
            if not obj.description:
                descriptions = {
                        0: _(u"Ingen begrunnelse. Kontakt %s for mer informasjon.") % obj.given_by.email,
                        1: _(u"Du har fått en prikk for et sosialt arrangement."),
                        2: _(u"Du har fått en prikk for en bedriftspresentasjon."),
                        3: _(u"Du har fått en prikk for et kurs."),
                        4: _(u"Du har fått en prikk fordi du ikke har levert tilbakemelding."),
                        5: _(u"Du har fått en prikk relatert til kontoret."), 
                    }
                obj.description = descriptions[obj.category]
                
        obj.last_changed_by = request.user
        obj.save()

admin.site.register(Mark, MarkAdmin)
