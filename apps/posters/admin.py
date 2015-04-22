from django.contrib import admin

from django.utils.translation import ugettext as _

from apps.posters.models import Poster

class PosterAdmin(admin.ModelAdmin):
    model = Poster
    list_display = ('title', 'category', 'company', 'when', 'assigned_to', 'display_from', 'display_to',
                    'ordered_date', 'ordered_by', 'ordered_committee')
    fieldsets = (
        (_(u'Event info'), {'fields': ('title', 'when', 'company','price', 'description')}),
        (_(u'Order info'), {'fields': ('category', 'amount', 'comments')}),
        (_(u'proKom'), {'fields': ('display_from', 'display_to', 'assigned_to', 'ordered_by', 'ordered_committee', 'finished')}),
    )
    search_fields = ('title', 'category', 'company', 'when')



admin.site.register(Poster, PosterAdmin)
#username, expiration_date, registered, note