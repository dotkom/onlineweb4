from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import UserNameSerializer
from apps.gallery.serializers import ResponsiveImageSerializer

from .models import Album, Photo, UserTag


class PhotoReadOnlySerializer(serializers.ModelSerializer):
    photographer = UserNameSerializer()
    tags = TagListSerializerField()
    image = ResponsiveImageSerializer()

    class Meta:
        model = Photo
        fields = (
            'id', 'album', 'relative_id', 'image', 'created_date', 'title', 'description', 'tags',
            'photographer_name', 'photographer', 'user_tags',
        )
        read_only = True


class AlbumReadOnlySerializer(serializers.ModelSerializer):
    created_by = UserNameSerializer()
    tags = TagListSerializerField()
    cover_photo = PhotoReadOnlySerializer()

    class Meta:
        model = Album
        fields = (
            'id', 'title', 'description', 'created_date', 'published_date', 'tags', 'photos', 'public', 'created_by',
            'cover_photo',
        )
        read_only = True


class UserTagReadOnlySerializer(serializers.ModelSerializer):
    user = UserNameSerializer()

    class Meta:
        model = UserTag
        fields = (
            'id', 'user', 'created_date', 'photo',
        )
        read_only = True


class UserTagCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    photo = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all())

    class Meta:
        model = UserTag
        fields = (
            'id', 'user', 'created_date', 'photo',
        )
