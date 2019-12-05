import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)

from apps.dashboard.tools import DashboardPermissionMixin
from apps.gallery.util import UploadImageHandler
from apps.photoalbum.dashboard.forms import AlbumCreateOrUpdateForm, PhotoCreateForm
from apps.photoalbum.models import Album, Photo

logger = logging.getLogger(__name__)


class Overview(DashboardPermissionMixin, TemplateView):
    template_name = "photoalbum/dashboard/index.html"
    permission_required = "photoalbum.view_album"


class AlbumsView(DashboardPermissionMixin, TemplateView):
    model = Album
    template_name = "photoalbum/dashboard/albums.html"
    permission_required = "photoalbum.change_album"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["albums"] = Album.objects.all().prefetch_related("photos")
        return context


class AlbumView(DashboardPermissionMixin, DetailView):
    model = Album
    template_name = "photoalbum/dashboard/album.html"
    permission_required = "photoalbum.view_album"


class AlbumCreate(DashboardPermissionMixin, CreateView):
    model = Album
    form_class = AlbumCreateOrUpdateForm
    template_name = "photoalbum/dashboard/album_update.html"
    permission_required = "photoalbum.add_album"

    def get_success_url(self):
        return reverse("dashboard-photoalbum:albums")

    def form_valid(self, form):
        album = form.save(commit=False)
        user = self.request.user
        album.created_by = user
        return super().form_valid(form)


class AlbumUpdate(DashboardPermissionMixin, UpdateView):
    model = Album
    form_class = AlbumCreateOrUpdateForm
    template_name = "photoalbum/dashboard/album_update.html"
    context_object_name = "album"
    permission_required = "photoalbum.change_album"

    def get_success_url(self):
        return reverse("dashboard-photoalbum:album", kwargs={"pk": self.object.pk})


class AlbumDelete(DashboardPermissionMixin, DeleteView):
    model = Album
    template_name = "photoalbum/dashboard/delete.html"
    permission_required = "photoalbum.delete_category"

    def get_success_url(self):
        return reverse("dashboard-photoalbum:albums")


class PhotoCreate(DashboardPermissionMixin, CreateView):
    model = Photo
    template_name = "photoalbum/dashboard/photo_update.html"
    context_object_name = "photo"
    permission_required = "photoalbum.add_photo"
    form_class = PhotoCreateForm

    def form_valid(self, form):
        photo = form.save(commit=False)
        user = self.request.user
        photo.created_by = user
        photo.album = get_object_or_404(Album, pk=self.kwargs.get("album_pk"))
        result = UploadImageHandler(self.request.FILES.get("file")).status
        if result:
            photo.raw_image = result.data

        if not photo.photographer_name:
            if photo.photographer:
                photo.photographer_name = photo.photographer.get_full_name()
            else:
                photo.photographer_name = user.get_full_name()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "dashboard-photoalbum:album", kwargs={"pk": self.object.album.pk}
        )


class PhotoUpdate(DashboardPermissionMixin, UpdateView):
    model = Photo
    fields = ("title", "description", "tags", "photographer_name", "photographer")
    template_name = "photoalbum/dashboard/photo_update.html"
    context_object_name = "photo"
    permission_required = "photoalbum.change_photo"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["photo"] = self.object
        return context

    def get_success_url(self):
        kwargs = {"pk": self.object.pk, "album_pk": self.object.album.pk}
        return reverse("dashboard-photoalbum:photo_update", kwargs=kwargs)


class PhotoDelete(DashboardPermissionMixin, DeleteView):
    model = Photo
    template_name = "photoalbum/dashboard/delete.html"
    permission_required = "photoalbum.delete_photo"

    def get_success_url(self):
        return reverse(
            "dashboard-photoalbum:album", kwargs={"pk": self.object.album.pk}
        )
