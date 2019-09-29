from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.photoalbum.models import Album


class AlbumAdmin(VersionAdmin):
    model = Album
    list_display = ['title', 'photos', 'tags']


admin.site.register(Album, AlbumAdmin)
