# -*- coding: utf-8 -*-
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from rest_framework import mixins, permissions, viewsets

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage

from .filters import AlbumFilter, PhotoFilter, UserTagFilter
from .forms import ReportPhotoForm
from .models import Album, Photo, UserTag
from .serializers import (AlbumCreateOrUpdateSerializer, AlbumReadOnlySerializer,
                          PhotoCreateOrUpdateSerializer, PhotoReadOnlySerializer,
                          UserTagCreateSerializer, UserTagReadOnlySerializer)
from .utils import report_photo


class AlbumsListView(ListView):
    model = Album
    template_name = 'photoalbum/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['albums'] = Album.objects_visible.all()

        return context


class AlbumDetailView(DetailView, View):

    model = Album
    template_name = "photoalbum/detail.html"

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
        album_pk = self.kwargs.get('pk')
        album = get_object_or_404(Album.objects_visible.all(), pk=album_pk)
        context['album'] = album

        return context


class PhotoDisplay(DetailView):
    model = Photo
    template_name = "photoalbum/photo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album_pk = self.kwargs.get('album_pk')
        photo_pk = self.kwargs.get('pk')

        photo = get_object_or_404(Photo, pk=photo_pk)
        album = get_object_or_404(Album.objects_visible.all(), pk=album_pk)

        previous_photo = album.get_previous_photo(photo)
        next_photo = album.get_next_photo(photo)

        context['photo'] = photo
        context['album'] = album
        context['form'] = ReportPhotoForm()
        context['previous_photo'] = previous_photo
        context['next_photo'] = next_photo

        return context


class PhotoReportFormView(SingleObjectMixin, FormView):
    model = ResponsiveImage
    template_name = 'photoalbum/photo.html'
    form_class = ReportPhotoForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(PhotoReportFormView, self).post(request, *args, **kwargs)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        photo = self.get_object()
        user = self.request.user
        cleaned_data = form.cleaned_data
        report_photo(cleaned_data['reason'], photo, user)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('photo_detail', kwargs={'pk': self.object.pk, 'album_pk': self.object.album.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photo'] = ResponsiveImage.objects.get(pk=self.kwargs['pk'])
        album = context['photo'].get_album()
        context['album'] = Album.objects.get(pk=album.pk)
        context['form'] = ReportPhotoForm()

        return context


class PhotoDetailView(View):

    def get(self, request, *args, **kwargs):
        view = PhotoDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PhotoReportFormView.as_view()
        return view(request, *args, **kwargs)


class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Album.objects_visible.all()
    filterset_class = AlbumFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AlbumCreateOrUpdateSerializer
        if self.action in ['list', 'retrieve']:
            return AlbumReadOnlySerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user: User = self.request.user
        if not user.is_authenticated:
            return Album.objects_public.all()
        return super().get_queryset()


class PhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Photo.objects.all()
    filterset_class = PhotoFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PhotoCreateOrUpdateSerializer
        if self.action in ['list', 'retrieve']:
            return PhotoReadOnlySerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user: User = self.request.user
        queryset = super().get_queryset()

        published_query = Q(album__published_date__lte=timezone.now())

        if not user.is_authenticated:
            return queryset.filter(published_query & Q(album__public=True))

        return queryset.filter(published_query)


class UserTagViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin):
    queryset = UserTag.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    filterset_class = UserTagFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return UserTagCreateSerializer
        if self.action in ['list', 'retrieve']:
            return UserTagReadOnlySerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user: User = self.request.user
        queryset = super().get_queryset()

        published_query = Q(photo__album__published_date__lte=timezone.now())

        if not user.is_authenticated:
            return queryset.filter(published_query & Q(photo__album__public=True))

        return queryset.filter(published_query)
