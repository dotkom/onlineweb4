from django.contrib import admin

# Register your models here.
from apps.photoalbum.models import Album, Photo



admin.site.register(Album)
admin.site.register(Photo)