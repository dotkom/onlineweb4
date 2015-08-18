from rest_framework import serializers

from apps.article.models import Article, Tag
from apps.authentication.serializers import UserSerializer


class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='created_by')  # serializers.StringRelatedField(source='created_by')
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Article
        fields = (
                'absolute_url', 'additional_authors', 'author', 'changed_date', 'content', 'created_date',
                'featured', 'heading', 'id',
                # 'image_article_front_featured', 'image_article_front_small', 'image_article_full', 'image_article_main', 'image_article_related',
                'ingress', 'ingress_short', 'photographers', 'published_date', 'slug', 'video', 'images', 'article_tags',
            )

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'short_name')
