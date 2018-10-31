from django.contrib import admin

from apps.contribution.models import Repository


class RepositoryAdmin(admin.ModelAdmin):
    model = Repository
    list_display = ['id', 'name', 'updated_at']

admin.site.register(Repository, RepositoryAdmin)
