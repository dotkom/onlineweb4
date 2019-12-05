import logging

from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import UserNameSerializer
from apps.gallery.fields import ImageField
from apps.gallery.serializers import ResponsiveImageSerializer

from .models import Album, Photo, UserTag

logger = logging.getLogger(__name__)


class PhotoReadOnlySerializer(serializers.ModelSerializer):
    photographer = UserNameSerializer()
    tags = TagListSerializerField()
    image = ResponsiveImageSerializer()

    class Meta:
        model = Photo
        fields = (
            "id",
            "album",
            "relative_id",
            "image",
            "created_date",
            "title",
            "description",
            "tags",
            "photographer_name",
            "photographer",
            "user_tags",
        )
        read_only = True


class PhotoCreateOrUpdateSerializer(serializers.ModelSerializer):
    photographer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    )
    title = serializers.CharField(required=False, default=None)
    tags = TagListSerializerField(required=False)
    raw_image = ImageField(required=True)
    album = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.all(), required=True
    )

    class Meta:
        model = Photo
        fields = (
            "id",
            "album",
            "relative_id",
            "image",
            "created_date",
            "title",
            "description",
            "tags",
            "raw_image",
            "photographer_name",
            "photographer",
        )
        read_only_fields = ("image", "created_date")


class AlbumReadOnlySerializer(serializers.ModelSerializer):
    created_by = UserNameSerializer()
    tags = TagListSerializerField()
    cover_photo = PhotoReadOnlySerializer()

    class Meta:
        model = Album
        fields = (
            "id",
            "title",
            "description",
            "created_date",
            "published_date",
            "tags",
            "photos",
            "public",
            "created_by",
            "cover_photo",
        )
        read_only = True


class AlbumCreateOrUpdateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = TagListSerializerField(required=False)
    cover_photo = PhotoReadOnlySerializer(required=False)
    published_date = serializers.DateTimeField(required=False)
    public = serializers.BooleanField(default=False)

    class Meta:
        model = Album
        fields = (
            "id",
            "title",
            "description",
            "created_date",
            "published_date",
            "tags",
            "public",
            "created_by",
            "cover_photo",
        )


class UserTagReadOnlySerializer(serializers.ModelSerializer):
    user = UserNameSerializer()

    class Meta:
        model = UserTag
        fields = ("id", "user", "created_date", "photo")
        read_only = True


class UserTagCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    photo = serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all())

    class Meta:
        model = UserTag
        fields = ("id", "user", "created_date", "photo")
