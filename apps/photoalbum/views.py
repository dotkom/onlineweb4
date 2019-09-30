# -*- coding: utf-8 -*-

from django.urls import reverse
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from rest_framework import permissions, viewsets

from apps.gallery.models import ResponsiveImage
from apps.photoalbum.forms import ReportPhotoForm
from apps.photoalbum.models import Album, Photo, UserTag
from apps.photoalbum.utils import get_next_photo, get_previous_photo, report_photo

from .serializers import AlbumReadOnlySerializer, PhotoReadOnlySerializer, UserTagReadOnlySerializer


class AlbumsListView(ListView):
    model = Album
    template_name = 'photoalbum/index.html'

    def get_context_data(self, **kwargs):
        context = super(AlbumsListView, self).get_context_data(**kwargs)
        context['albums'] = Album.objects.all()

        return context


class AlbumDetailView(DetailView, View):

    model = Album
    template_name = "photoalbum/detail.html"

    def get_context_data(self, **kwargs):
        context = super(AlbumDetailView, self).get_context_data(**kwargs)

        album = Album.objects.get(pk=self.kwargs['pk'])
        context['album'] = album

        return context


class PhotoDisplay(DetailView):
    model = ResponsiveImage
    template_name = "photoalbum/photo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = ResponsiveImage.objects.get(pk=self.kwargs['pk'])
        album = Album.objects.get(pk=self.kwargs['album_pk'])

        context['photo'] = photo
        context['album'] = album
        context['form'] = ReportPhotoForm()
        context['tagged_users'] = context['photo'].tags
        context['next_photo'] = get_next_photo(photo, album)
        context['previous_photo'] = get_previous_photo(photo, album)

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
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Album.objects.all()
    filterset_fields = ('published_date',)
    serializer_class = AlbumReadOnlySerializer


class AlbumPhotoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    serializer_class = PhotoReadOnlySerializer
    queryset = Photo.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        album_id = self.kwargs.get('album_id', None)

        if album_id:
            return queryset.filter(album_id=album_id)

        return queryset.none()


class PhotoUserTagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = UserTag.objects.all()
    filterset_fields = ('published_date',)
    serializer_class = UserTagReadOnlySerializer
