# -*- coding: utf-8 -*-

from chunks.models import Chunk

from rest_framework import serializers


class ChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chunk

        fields = (
            'key', 'content', 'description', 'pk',
        )
