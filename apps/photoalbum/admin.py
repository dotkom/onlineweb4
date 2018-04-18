
"""
from django.contrib import admin
from reversion.admin import VersionAdmin

# Register your models here.
from apps.photoalbum.models import Album

class AlbumAdmin(VersionAdmin):
	model = Album
	#list_display = ['title', 'photos', 'tags']
	fieldsets = (
		#(None, {'fields': ('title', 'photos', 'tags')})
	)

admin.site.register(Album, AlbumAdmin)
"""