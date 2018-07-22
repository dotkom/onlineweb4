# -*- coding: utf-8 -*-

from apps.chunksapi.serializers import ChunkSerializer

from chunks.models import Chunk
from rest_framework import mixins, viewsets
from rest_framework.views import APIView


class ChunkViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, APIView):
    queryset = Chunk.objects.all()
    model = Chunk
    serializer_class = ChunkSerializer
