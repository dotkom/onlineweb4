from django.contrib import admin

from django.utils.translation import ugettext as _

from apps.posters.models import Poster, GeneralOrder

class PosterAdmin(admin.ModelAdmin):
    model = Poster
    list_display = ('event', 'assigned_to', 'display_from', 'display_to',
                    'ordered_date', 'ordered_by', 'ordered_committee')
    fieldsets = (
        (_(u'Event info'), {'fields': ('event', 'price', 'description')}),
        (_(u'Order info'), {'fields': ('amount', 'comments')}),
        (_(u'proKom'), {'fields': ('display_from', 'display_to', 'assigned_to', 'ordered_by', 'ordered_committee', 'finished')}),
    )
    search_fields = ('title', 'category', 'company', 'when')



admin.site.register(Poster, PosterAdmin)
admin.site.register(GeneralOrder)
#username, expiration_date, registered, note