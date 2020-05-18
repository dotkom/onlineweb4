from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.photoalbum.models import Album, Photo, UserTag


class PhotoInlineAdmin(admin.TabularInline):
    model = Photo
    extra = 0
    fields = ("title",)
    readonly_fields = ("title",)


@admin.register(Album)
class AlbumAdmin(VersionAdmin):
    model = Album
    inlines = (PhotoInlineAdmin,)
    list_display = ("title", "published_date", "created_by")
    search_fields = (
        "title",
        "tags__name",
        "published_date",
        "created_by__first_name",
        "description",
    )


class UserTagInlineAdmin(admin.StackedInline):
    model = UserTag
    extra = 0


@admin.register(Photo)
class PhotoAdmin(VersionAdmin):
    model = Photo
    list_display = ("title", "album", "photographer", "photographer_name")
    search_fields = (
        "title",
        "album",
        "photographer",
        "photographer_name",
        "tags__name",
        "description",
    )
    inlines = (UserTagInlineAdmin,)
