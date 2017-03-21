from django.contrib import admin
from reversion.admin import VersionAdmin

from apps.article.models import Article


class ArticleAdmin(VersionAdmin):
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
