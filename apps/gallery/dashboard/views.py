# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from django.shortcuts import render
from django.views.generic import View, DetailView

from apps.dashboard.tools import DashboardMixin, DashboardPermissionMixin
from apps.gallery.models import UnhandledImage, ResponsiveImage


class GalleryIndex(View, DashboardPermissionMixin):
    """
    GalleryIndex renders the dashboard start page for the Gallery app,
    which allows administrators and staff to upload, edit and delete
    ResponsiveImages.
    """

    template_name = 'gallery/dashboard/index.html'
    model = ResponsiveImage

    def get(self, request, **kwargs):
        """
        Regular requests to this view renders the index page.
        :param request: Django Request instance
        :param kwargs: KeyWord arguments
        :return: Rendered HttpResponse
        """

        return render(request, self.template_name, self.get_context_data(kwargs))


class GalleryUnhandledIndex(GalleryIndex):
    template_name = 'gallery/dashboard/unhandled_index.html'
    model = UnhandledImage
