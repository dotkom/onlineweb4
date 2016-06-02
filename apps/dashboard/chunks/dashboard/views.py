from chunks.models import Chunk
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.dashboard.tools import DashboardPermissionMixin


class ChunkList(DashboardPermissionMixin, ListView):
    model = Chunk
    queryset = Chunk.objects.all()
    context_object_name = 'chunks'
    permission_required = 'chunks.add_chunk'


class ChunkUpdate(DashboardPermissionMixin, UpdateView):
    model = Chunk
    context_object_name = 'chunk'
    fields = ('key', 'description', 'content')
    permission_required = 'chunks.change_chunk'
    success_url = reverse_lazy('chunk-dashboard:list')


class ChunkCreate(DashboardPermissionMixin, CreateView):
    model = Chunk
    fields = ('key', 'description', 'content')
    permission_required = 'chunks.add_chunk'

    def get_success_url(self):
        return reverse('chunk-dashboard:update', args=(self.object.id,))


class ChunkDelete(DashboardPermissionMixin, DeleteView):
    model = Chunk
    permission_required = ('chunks.delete_chunk',)
    success_url = reverse_lazy('chunk-dashboard:list')
