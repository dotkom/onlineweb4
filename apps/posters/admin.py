from django.contrib import admin

from django.utils.translation import ugettext as _

from apps.posters.models import Poster

class PosterAdmin(admin.ModelAdmin):
    model = Poster
    list_display = ('title', 'category', 'company', 'when', 'assigned_to', 'display_from', 'display_to',
                    'ordered_date', 'ordered_by', 'ordered_committee')
    fieldsets = (
        (None, {'fields': ('username', 'registered', 'expiration_date')}),
        (_(u'Notater'), {'fields': ('note', 'description')}),

    )
    search_fields = ('title', 'category', 'company', 'when')



admin.site.register(Poster, PosterAdmin)