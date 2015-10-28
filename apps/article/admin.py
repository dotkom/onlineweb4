from django.contrib import admin
from apps.article.models import Article, Tag, ArticleTag
from django.conf import settings
from filebrowser.settings import VERSIONS, ADMIN_THUMBNAIL

from reversion.admin import VersionAdmin


class ArticleTagAdmin(VersionAdmin):
    model = ArticleTag


class ArticleTagInline(admin.TabularInline):
    model = ArticleTag
    max_num = 99
    extra = 0


class TagAdmin(VersionAdmin):
    def save_model(self, request, obj, form, change):
        obj.changed_by = request.user
        if not change:
            obj.name = obj.name.replace('.', '')
            obj.created_by = request.user
        obj.save()


class ArticleAdmin(VersionAdmin):
    inlines = (ArticleTagInline,)
    list_display = ("heading", "created_by", "changed_by")

    # set the created and changed by fields
    def save_model(self, request, obj, form, change):

        obj.changed_by = request.user

        if not change:
            obj.created_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instances in instances:
            instances.save()

admin.site.register(Article, ArticleAdmin)
admin.site.register(Tag, TagAdmin)
