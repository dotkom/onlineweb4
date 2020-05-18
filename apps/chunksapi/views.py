# -*- coding: utf-8 -*-

from chunks.models import Chunk
from rest_framework import mixins, viewsets
from rest_framework.views import APIView

from apps.chunksapi.serializers import ChunkSerializer


class ChunkViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, APIView
):
    queryset = Chunk.objects.all()
    model = Chunk
    serializer_class = ChunkSerializer
    filterset_fields = ("key",)
    pagination_class = None
