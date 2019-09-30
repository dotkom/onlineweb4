from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField

from apps.authentication.serializers import UserNameSerializer

from .models import Album, Photo, UserTag


class PhotoReadOnlySerializer(serializers.ModelSerializer):
    photographer = UserNameSerializer()
    tags = TagListSerializerField()

    class Meta:
        model = Photo
        fields = (
            'id', 'title', 'description', 'tags', 'photographer_name', 'photographer',
        )
        read_only = True


class AlbumReadOnlySerializer(serializers.ModelSerializer):
    created_by = UserNameSerializer()
    tags = TagListSerializerField()
    cover_photo = PhotoReadOnlySerializer()

    class Meta:
        model = Album
        fields = (
            'id', 'created_date', 'title', 'description', 'created_by', 'published_date', 'tags', 'photos',
            'cover_photo',
        )
        read_only = True


class UserTagReadOnlySerializer(serializers.ModelSerializer):
    user = UserNameSerializer()

    class Meta:
        model = UserTag
        fields = (
            'id', 'user', 'created_date',
        )
        read_only = True
