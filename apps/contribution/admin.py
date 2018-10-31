from django.contrib import admin

from apps.contribution.models import Repository, RepositoryLanguage


class LanguagesInLine(admin.TabularInline):
    model = RepositoryLanguage
    extra = 0


class RepositoryAdmin(admin.ModelAdmin):
    model = Repository
    ordering = ['-updated_at']
    list_display = ['id', 'name', 'updated_at']
    inlines = [
        LanguagesInLine,
    ]


admin.site.register(Repository, RepositoryAdmin)
