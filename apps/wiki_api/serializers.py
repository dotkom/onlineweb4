from rest_framework import serializers
from wiki.models import Article, ArticleRevision, URLPath

from apps.authentication.serializers import UserNameSerializer
from apps.wiki_api.fields import WikiPermissionField


class PreviousArticleRevisionReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRevision
        fields = ('id', 'title',)
        read_only = True


class ArticleRevisionReadOnlySerializer(serializers.ModelSerializer):
    user = UserNameSerializer(read_only=True)
    previous_revision = PreviousArticleRevisionReadOnlySerializer(read_only=True)

    class Meta:
        model = ArticleRevision
        fields = (
            'id', 'title', 'content', 'revision_number', 'user_message', 'automatic_log', 'ip_address', 'modified',
            'created', 'previous_revision', 'deleted', 'locked', 'user',
        )
        read_only = True


class ArticleReadOnlySerializer(serializers.ModelSerializer):
    owner = UserNameSerializer(read_only=True)

    current_revision = ArticleRevisionReadOnlySerializer(read_only=True)

    can_read = WikiPermissionField()
    can_write = WikiPermissionField()
    can_delete = WikiPermissionField()
    can_moderate = WikiPermissionField()
    can_assign = WikiPermissionField()

    class Meta:
        model = Article
        fields = (
            'group_read', 'group_write', 'other_read', 'other_write', 'created', 'modified', 'owner', 'group',
            'can_read', 'can_write', 'can_delete', 'can_moderate', 'can_assign', 'current_revision',
        )
        read_only = True


class RelatedURLPathSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj: URLPath):
        return obj.get_absolute_url()

    class Meta:
        model = URLPath
        fields = ('slug', 'absolute_url',)


class URLPathReadOnlySerializer(serializers.ModelSerializer):
    article = ArticleReadOnlySerializer()
    parent = RelatedURLPathSerializer()
    moved_to = RelatedURLPathSerializer()

    absolute_url = serializers.SerializerMethodField()
    children = RelatedURLPathSerializer(many=True)

    def get_absolute_url(self, obj: URLPath):
        return obj.get_absolute_url()

    class Meta:
        model = URLPath
        fields = ('article', 'slug', 'parent', 'moved_to', 'path', 'is_deleted', 'absolute_url', 'children')
        read_only = True
