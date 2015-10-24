# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from django.views.generic import DetailView, ListView, TemplateView

from apps.dashboard.tools import DashboardPermissionMixin
from apps.gallery.models import UnhandledImage, ResponsiveImage


class GalleryIndex(DashboardPermissionMixin, ListView):
    """
    GalleryIndex renders the dashboard start page for the Gallery app,
    which allows administrators and staff to upload, edit and delete
    ResponsiveImages.
    """

    permission_required = 'gallery.view_responsiveimage'
    template_name = 'gallery/dashboard/index.html'
    queryset = ResponsiveImage.objects.all().order_by('-timestamp')
    context_object_name = 'images'

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data of this view
        """

        # We would like to add years to our index to enable filterbuttons
        context = super(GalleryIndex, self).get_context_data(**kwargs)
        context['years'] = set(img.timestamp.year for img in self.queryset)

        return context


class GalleryDetail(DetailView, DashboardPermissionMixin):
    """
    GalleryDetail renders the dashboard detail page for the Gallery app,
    which allows administrators to upload, edit and delete
    ResponsiveImages.
    """

    permission_required = 'gallery.change_responsiveimage'
    template_name = 'gallery/dashboard/detail.html'
    model = ResponsiveImage
    context_object_name = 'image'


class GalleryUpload(TemplateView, DashboardPermissionMixin):
    """
    GalleryUpload renders the dashboard upload page for the Gallery app,
    which facilitates upload, cropping and version generation of images.
    """

    permission_required = 'gallery.add_responsiveimage'
    template_name = 'gallery/dashboard/upload.html'


class GalleryUnhandledIndex(GalleryIndex):
    """
    GalleryUnhandledIndex renders the dashboard list page for the Gallery app's
    list view of images that have not yet been cropped and stored after upload.
    Administrators may remove images from this view.
    """

    permission_required = 'gallery.view_unhandledimage'
    template_name = 'gallery/dashboard/unhandled_index.html'
    queryset = UnhandledImage.objects.all()
    context_object_name = 'images'
