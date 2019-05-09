from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from apps.article.models import Article
from apps.authentication.serializers import UserSerializer
from apps.gallery.serializers import ResponsiveImageSerializer


class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    created_by = UserSerializer()
    image = ResponsiveImageSerializer()
    tags = TagListSerializerField()
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Article
        fields = (
            'absolute_url',
            'authors',
            'created_by',
            'changed_date',
            'content',
            'created_date',
            'featured',
            'heading',
            'id',
            'ingress',
            'ingress_short',
            'published_date',
            'slug',
            'tags',
            'video',
            'image'
        )
