# -*- coding: utf-8 -*-
from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, permissions, viewsets

from apps.authentication.models import OnlineUser as User

from .filters import AlbumFilter, PhotoFilter, UserTagFilter
from .models import Album, Photo, UserTag
from .serializers import (
    AlbumCreateOrUpdateSerializer,
    AlbumListSerializer,
    AlbumRetrieveSerializer,
    PhotoCreateOrUpdateSerializer,
    PhotoListSerializer,
    PhotoRetrieveSerializer,
    UserTagCreateSerializer,
    UserTagListSerializer,
    UserTagRetrieveSerializer,
)


class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Album.objects.all()
    filterset_class = AlbumFilter

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AlbumCreateOrUpdateSerializer
        if self.action in ["retrieve"]:
            return AlbumRetrieveSerializer
        if self.action in ["list"]:
            return AlbumListSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user: User = self.request.user
        queryset = super().get_queryset()

        if user.has_perm("photoalbum.view_album"):
            return queryset

        published_query = Q(published_date__lte=timezone.now())

        if not user.is_authenticated:
            return queryset.filter(published_query & Q(public=True))

        return queryset.filter(published_query)


class PhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Photo.objects.all()
    filterset_class = PhotoFilter

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PhotoCreateOrUpdateSerializer
        if self.action in ["retrieve"]:
            return PhotoRetrieveSerializer
        if self.action in ["list"]:
            return PhotoListSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user: User = self.request.user
        queryset = super().get_queryset()

        if user.has_perm("photoalbum.view_photo"):
            return queryset

        published_query = Q(album__published_date__lte=timezone.now())

        if not user.is_authenticated:
            return queryset.filter(published_query & Q(album__public=True))

        return queryset.filter(published_query)


class UserTagViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = UserTag.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = UserTagFilter

    def get_serializer_class(self):
        if self.action == "create":
            return UserTagCreateSerializer
        if self.action in ["retrieve"]:
            return UserTagRetrieveSerializer
        if self.action in ["list"]:
            return UserTagListSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user: User = self.request.user
        queryset = super().get_queryset()

        if user.has_perm("photoalbum.view_usertag"):
            return queryset

        published_query = Q(photo__album__published_date__lte=timezone.now())

        if not user.is_authenticated:
            return queryset.filter(published_query & Q(photo__album__public=True))

        return queryset.filter(published_query)
