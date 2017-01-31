from chunks.models import Chunk
from django.contrib import admin
from django.db.models import Q
from reversion.admin import VersionAdmin

from apps.offline.models import Issue, ProxyChunk


class ProxyChunkAdmin(VersionAdmin):

    readonly_fields = ['key']

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        offline = Chunk.objects.filter(Q(key='offline_ingress') | Q(key='offline_brodtekst'))
        return offline


admin.site.register(ProxyChunk, ProxyChunkAdmin)
admin.site.register(Issue)
