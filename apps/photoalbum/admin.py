from django.contrib import admin
from reversion.admin import VersionAdmin

# Register your models here.
from apps.photoalbum.models import Album, Photo, AlbumTag, AlbumToPhoto, UserTagToPhoto, TagsToAlbum

class AlbumAdmin(VersionAdmin):
	model = Album
	#list_display = ['title', 'photos', 'tags']
	fieldsets = (
		#(None, {'fields': ('title', 'photos', 'tags')})
	)

admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo)
admin.site.register(AlbumTag)
admin.site.register(AlbumToPhoto)
admin.site.register(UserTagToPhoto)
admin.site.register(TagsToAlbum)