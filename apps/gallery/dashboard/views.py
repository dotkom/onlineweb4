# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/24/15

from logging import getLogger

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView, UpdateView
from taggit.models import TaggedItem

from apps.dashboard.tools import DashboardPermissionMixin
from apps.gallery.dashboard.forms import ResponsiveImageForm
from apps.gallery.models import ResponsiveImage, UnhandledImage
from utils.helpers import humanize_size


class GalleryIndex(DashboardPermissionMixin, ListView):
    """
    GalleryIndex renders the dashboard start page for the Gallery app,
    which allows administrators and staff to upload, edit and delete
    ResponsiveImages.
    """

    permission_required = "gallery.view_responsiveimage"
    template_name = "gallery/dashboard/index.html"
    queryset = ResponsiveImage.objects.all().order_by("-timestamp")[:15]
    context_object_name = "images"

    def get_context_data(self, **kwargs):
        """
        Retrieves the context data of this view
        """

        # We would like to add years to our index to enable filterbuttons
        context = super(GalleryIndex, self).get_context_data(**kwargs)

        years = set()
        total_disk_usage = 0

        # We cannot re-use the self.queryset, as it contains cached instances that might be deleted,
        # thus causing the file size summation to fail due to missing files.
        for img in ResponsiveImage.objects.all():
            years.add(img.timestamp.year)
            if img.id:
                try:
                    total_disk_usage += img.sizeof_total_raw()
                except OSError as e:
                    getLogger(__name__).error(
                        "GalleryIndex file summation on missing file: %s" % e
                    )

        # Filter out potential ResponsiveImage objects that have orphan file references
        context["images"] = [i for i in context["images"] if i.file_status_ok()]

        # Add query filters and some statistics on disk usage
        context["years"] = years
        context["tags"] = sorted(
            set(
                tag.tag.name
                for tag in TaggedItem.objects.filter(
                    content_type=ContentType.objects.get_for_model(ResponsiveImage)
                ).order_by("tag__name")
            )
        )
        context["disk_usage"] = humanize_size(total_disk_usage)

        return context


class GalleryDetail(DashboardPermissionMixin, UpdateView):
    """
    GalleryDetail renders the dashboard detail page for the Gallery app,
    which allows administrators to upload, edit and delete
    ResponsiveImages.
    """

    permission_required = "gallery.change_responsiveimage"
    accept_global_perms = True
    template_name = "gallery/dashboard/detail.html"
    model = ResponsiveImage
    context_object_name = "image"
    form_class = ResponsiveImageForm

    def form_valid(self, form):
        """
        Add success message
        """

        messages.success(self.request, "Bildet ble oppdatert.")
        getLogger(__name__).info(
            "%s updated ResponsiveImage %d" % (self.request.user, self.object.id)
        )

        return super(GalleryDetail, self).form_valid(form)

    def form_invalid(self, form):
        """
        Add error message if invalid
        """

        messages.error(self.request, "Noen av feltene inneholder feil.")

        return super(GalleryDetail, self).form_invalid(form)

    def get_success_url(self):
        """
        We override the get_success_url method, since we do not want to invoke
        a potential get_absolute_url on the model, since the absolute url of
        the image should be the path to the LG version.
        """

        return reverse("gallery_dashboard:detail", kwargs={"pk": self.object.id})

    def get_object(self, queryset=None):
        """
        We override the get_object to inject an extra health-check on the status of the files toe
        ResponsiveImage objects's ImageField point to. This to be able to insert error messages
        to the user, prompting them to delete broken objects.
        """

        obj = super().get_object(queryset=queryset)

        if not obj.file_status_ok():
            messages.error(
                self.request, "Dette bildeobjektet er korrupt/ødelagt og bør slettes!"
            )

        return obj


class GalleryUpload(DashboardPermissionMixin, TemplateView):
    """
    GalleryUpload renders the dashboard upload page for the Gallery app,
    which facilitates upload, cropping and version generation of images.
    """

    permission_required = "gallery.add_responsiveimage"
    template_name = "gallery/dashboard/upload.html"


class GalleryUnhandledIndex(DashboardPermissionMixin, ListView):
    """
    GalleryUnhandledIndex renders the dashboard list page for the Gallery app's
    list view of images that have not yet been cropped and stored after upload.
    Administrators may remove images from this view.
    """

    permission_required = "gallery.view_unhandledimage"
    template_name = "gallery/dashboard/unhandled.html"
    queryset = UnhandledImage.objects.all()
    context_object_name = "images"

    def post(self, request, *args, **kwargs):
        if "action" in request.POST and request.POST["action"] == "delete_all":
            if self.queryset:
                self.queryset.delete()
                messages.success(request, "Alle ubehandlede bilder ble slettet")

                getLogger(__name__).info(
                    "%s deleted all UnhandledImage instances" % self.request.user
                )

                return redirect(reverse("gallery_dashboard:unhandled"))
            else:
                messages.warning(request, "Fant ingen bilder. Ingen operasjon utført.")
                return redirect(reverse("gallery_dashboard:unhandled"))
        else:
            return HttpResponseBadRequest("Bad request")


class GalleryDelete(DashboardPermissionMixin, DetailView):
    """
    GalleryDelete facilitates removal of ResponsiveImages
    """

    permission_required = "gallery.delete_responsiveimage"
    accept_global_perms = True
    model = ResponsiveImage

    def get(self, request, *args, **kwargs):
        """
        GET request are forbidden on delete views
        :param request: Django Request instance
        :param args: Positional arguments
        :param kwargs: Keyword arguments
        :return: 405 Method Not Allowed
        """

        return HttpResponseNotAllowed(permitted_methods=["POST"])

    def post(self, request, *args, **kwargs):
        img = self.get_object(queryset=self.model.objects.all())
        if img:
            image_name = img.name
            image_id = img.id
            img.delete()
            messages.success(request, "%s (%d) ble slettet." % (image_name, image_id))

            getLogger(__name__).info(
                "%s deleted ResponsiveImage %d" % (self.request.user, image_id)
            )

            return redirect(reverse("gallery_dashboard:index"))
        else:
            messages.error(request, "Det oppstod en feil, klarte ikke slette bildet.")
            getLogger(__name__).error(
                "%s attempted to delete image with ID %d, but failed as queryset was empty."
                % (self.request.user, kwargs["pk"])
            )

            return redirect(reverse("gallery_dashboard:detail", **kwargs))


class GalleryUnhandledDelete(DashboardPermissionMixin, DetailView):
    """
    GalleryUnhandledDelete facilitates removal of UnhandledImages
    """

    permission_required = "gallery.delete_unhandledimage"
    accept_global_perms = True
    model = UnhandledImage

    def get(self, request, *args, **kwargs):
        """
        GET request are forbidden on delete views
        :param request: Django Request instance
        :param args: Positional arguments
        :param kwargs: Keyword arguments
        :return: 405 Method Not Allowed
        """

        return HttpResponseNotAllowed(permitted_methods=["POST"])

    def post(self, request, *args, **kwargs):
        img = self.get_object(queryset=self.model.objects.all())
        if img:
            image_id = img.id
            img.delete()
            messages.success(request, "Ubehandlet bilde %d ble slettet." % image_id)

            getLogger(__name__).info(
                "%s deleted UnhandledImage %d" % (self.request.user, image_id)
            )

            return redirect(reverse("gallery_dashboard:unhandled"))
        else:
            messages.error(request, "Det oppstod en feil, klarte ikke slette bildet.")
            getLogger(__name__).error(
                "%s attempted to delete image with ID %d, but failed as queryset was empty."
                % (self.request.user, kwargs["pk"])
            )

            return redirect(reverse("gallery_dashboard:unhandled"))
