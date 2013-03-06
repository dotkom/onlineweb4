from apps.offline.models import ProxyChunk, Issue
from chunks.models import Chunk
from django.contrib import admin
from django.db.models import Q


class ProxyChunkAdmin(admin.ModelAdmin):

    readonly_fields = ['key']

    def queryset(self, request):
        offline = Chunk.objects.filter(Q(key='offline_ingress') | Q(key='offline_brodtekst'))
        return offline

admin.site.register(ProxyChunk, ProxyChunkAdmin)
admin.site.register(Issue)
