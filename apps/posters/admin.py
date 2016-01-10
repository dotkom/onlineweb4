from django.contrib import admin

from django.utils.translation import ugettext as _

from apps.posters.models import Poster

from reversion.admin import VersionAdmin


class PosterAdmin(VersionAdmin):
    model = Poster
    list_display = ('event', 'title', 'assigned_to', 'display_from',
                    'ordered_date', 'ordered_by', 'ordered_committee')
    fieldsets = (
        (_(u'Event info'), {'fields': ('event', 'title', 'price', 'description', 'comments')}),
        (_(u'Order info'), {'fields': ('amount',)}),
        (_(u'proKom'), {'fields': ('display_from', 'assigned_to', 'ordered_by', 'ordered_committee', 'finished')}),
    )
    search_fields = ('title', 'category', 'company', 'when')


admin.site.register(Poster, PosterAdmin)
# username, expiration_date, registered, note
