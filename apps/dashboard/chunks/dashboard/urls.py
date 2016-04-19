from django.conf.urls import url

from apps.dashboard.chunks.dashboard.views import ChunkCreate, ChunkList, ChunkUpdate

urlpatterns = [
    url(r'^$', ChunkList.as_view(), name='list'),
    url(r'^chunk/create/$', ChunkCreate.as_view(), name='create'),
    url(r'^chunk/(?P<pk>\d+)/$', ChunkUpdate.as_view(), name='update'),
]
