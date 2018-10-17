# -*- coding: utf-8 -*-

from chunks.models import Chunk
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.views import APIView

from apps.chunksapi.serializers import ChunkSerializer


class ChunkViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, APIView):
    queryset = Chunk.objects.all()
    model = Chunk
    serializer_class = ChunkSerializer
    search_fields = ('^key', )
    filter_fields = ('key', )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    pagination_class = None
