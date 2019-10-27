# -*- encoding: utf-8 -*-

# API v1
from apps.api.utils import SharedAPIRootRouter
from apps.chunksapi import views

urlpatterns = []

router = SharedAPIRootRouter()
router.register("chunks", views.ChunkViewSet)
