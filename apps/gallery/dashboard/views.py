# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect
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


class GalleryUpload(DashboardPermissionMixin, TemplateView):
    """
    GalleryUpload renders the dashboard upload page for the Gallery app,
    which facilitates upload, cropping and version generation of images.
    """

    permission_required = 'gallery.add_responsiveimage'
    template_name = 'gallery/dashboard/upload.html'


class GalleryUnhandledIndex(DashboardPermissionMixin, ListView):
    """
    GalleryUnhandledIndex renders the dashboard list page for the Gallery app's
    list view of images that have not yet been cropped and stored after upload.
    Administrators may remove images from this view.
    """

    permission_required = 'gallery.view_unhandledimage'
    template_name = 'gallery/dashboard/unhandled.html'
    queryset = UnhandledImage.objects.all()
    context_object_name = 'images'

    def post(self, request, *args, **kwargs):
        if 'action' in request.POST and request.POST['action'] == 'delete_all':
            if self.queryset:
                self.queryset.delete()
                messages.success(request, u'Alle bilder ble slettet')
                return redirect(reverse('gallery_dashboard:unhandled'))
            else:
                messages.warning(request, u'Fant ingen bilder. Ingen operasjon utført.')
                return redirect(reverse('gallery_dashboard:unhandled'))
        else:
            return HttpResponseBadRequest()


class GalleryDelete(DashboardPermissionMixin, DetailView):
    """
    GalleryDelete facilitates removal of ResponsiveImages
    """

    permission_required = 'gallery.delete_responsiveimage'
    model = ResponsiveImage

    def get(self, request, *args, **kwargs):
        """
        GET request are forbidden on delete views
        :param request: Django Request instance
        :param args: Positional arguments
        :param kwargs: Keyword arguments
        :return: 405 Method Not Allowed
        """

        return HttpResponseNotAllowed(permitted_methods=['POST'])

    def post(self, request, *args, **kwargs):
        img = self.get_object(queryset=self.model.objects.all())
        if img:
            image_name = img.name
            image_id = img.id
            img.delete()
            messages.error(request, u'%s (%d) ble slettet.' % (image_name, image_id))

            return redirect(reverse('gallery_dashboard:index'))
        else:
            messages.error(request, u'Det oppstod en feil, klarte ikke slette bildet.')

            return redirect(reverse('gallery_dashboard:index'))


class GalleryUnhandledDelete(GalleryDetail):
    """
    GalleryUnhandledDelete facilitates removal of UnhandledImages
    """

    permission_required = 'gallery.delete_unhandledimage'
    model = UnhandledImage

    def post(self, request, *args, **kwargs):
        img = self.get_object(queryset=self.model.objects.all())
        if img:
            image_id = img.id
            img.delete()
            messages.success(request, u'Ubehandlet bilde %d ble slettet.' % image_id)
            return redirect(reverse('gallery_dashboard:unhandled'))
        else:
            messages.error(request, u'Det oppstod en feil, klarte ikke slette bildet.')
            return redirect(reverse('gallery_dashboard:unhandled'))
