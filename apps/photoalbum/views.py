# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from rest_framework import mixins, permissions, viewsets

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage
from apps.photoalbum.forms import ReportPhotoForm
from apps.photoalbum.models import Album, Photo
from apps.photoalbum.utils import report_photo

from .serializers import (AlbumReadOnlySerializer, PhotoReadOnlySerializer, UserTagCreateSerializer,
                          UserTagReadOnlySerializer)


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


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Album.objects_visible.all()
    filterset_fields = ('published_date',)
    serializer_class = AlbumReadOnlySerializer

    def get_queryset(self):
        user: User = self.request.user
        if not user.is_authenticated:
            return Album.objects_public.all()
        return super().get_queryset()


class AlbumPhotoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PhotoReadOnlySerializer

    def get_queryset(self):
        user: User = self.request.user
        album_queryset = Album.objects_visible.all()
        if not user.is_authenticated:
            album_queryset = Album.objects_public.all()

        album_pk = self.kwargs.get('album_pk', None)
        album = get_object_or_404(album_queryset, pk=album_pk)

        return album.photos.all()


class PhotoUserTagViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin):

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserTagCreateSerializer
        if self.action in ['list', 'retrieve']:
            return UserTagReadOnlySerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user: User = self.request.user
        album_queryset = Album.objects_visible.all()
        if not user.is_authenticated:
            album_queryset = Album.objects_public.all()

        album_pk = self.kwargs.get('album_pk', None)
        photo_pk = self.kwargs.get('photo_pk', None)

        album = get_object_or_404(album_queryset, pk=album_pk)
        photo = get_object_or_404(album.photos.all(), pk=photo_pk)

        return photo.user_tags.all()
