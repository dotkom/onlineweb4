from django.urls import re_path

from apps.dashboard.chunks.dashboard.views import (
    ChunkCreate,
    ChunkDelete,
    ChunkList,
    ChunkUpdate,
)

app_name = "chunks"

urlpatterns = [
    re_path(r"^$", ChunkList.as_view(), name="list"),
    re_path(r"^chunk/create/$", ChunkCreate.as_view(), name="create"),
    re_path(r"^chunk/(?P<pk>\d+)/$", ChunkUpdate.as_view(), name="update"),
    re_path(r"^chunk/(?P<pk>\d+)/delete/$", ChunkDelete.as_view(), name="delete"),
]
