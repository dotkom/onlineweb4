# -*- coding: utf-8 -*-
from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, permissions, viewsets

from apps.authentication.models import OnlineUser as User
from apps.common.rest_framework.mixins import MultiSerializerMixin

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


class AlbumViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Album.objects.all()
    filterset_class = AlbumFilter
    serializer_classes = {
        "write": AlbumCreateOrUpdateSerializer,
        "retrieve": AlbumRetrieveSerializer,
        "list": AlbumListSerializer,
    }

    def get_queryset(self):
        user: User = self.request.user
        queryset = super().get_queryset()

        if user.has_perm("photoalbum.view_album"):
            return queryset

        published_query = Q(published_date__lte=timezone.now())

        if not user.is_authenticated:
            return queryset.filter(published_query & Q(public=True))

        return queryset.filter(published_query)


class PhotoViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Photo.objects.all()
    filterset_class = PhotoFilter
    serializer_classes = {
        "write": PhotoCreateOrUpdateSerializer,
        "retrieve": PhotoRetrieveSerializer,
        "list": PhotoListSerializer,
    }

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
    MultiSerializerMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = UserTag.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = UserTagFilter
    serializer_classes = {
        "create": UserTagCreateSerializer,
        "retrieve": UserTagRetrieveSerializer,
        "list": UserTagListSerializer,
    }

    def get_queryset(self):
        user: User = self.request.user
        queryset = super().get_queryset()

        if user.has_perm("photoalbum.view_usertag"):
            return queryset

        published_query = Q(photo__album__published_date__lte=timezone.now())

        if not user.is_authenticated:
            return queryset.filter(published_query & Q(photo__album__public=True))

        return queryset.filter(published_query)
