from rest_framework import serializers

from apps.article.models import Article, Tag
from apps.authentication.serializers import UserSerializer
from apps.gallery.serializers import ResponsiveImageSerializer


class ArticleSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    image = ResponsiveImageSerializer()
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta(object):
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
            'photographers',
            'published_date',
            'slug',
            'video',
            'image',
            'article_tags',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Tag
        fields = ('name', 'short_name')
