from django.db import models
from django.utils.translation import ugettext_lazy as _
from filebrowser.fields import FileBrowseField

from apps.gallery.models import ResponsiveImage


class Company(models.Model):

    IMAGE_FOLDER = "images/companies"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

    name = models.CharField(_("bedriftsnavn"), max_length=100)
    short_description = models.TextField(_("kort beskrivelse"))
    long_description = models.TextField(_("utdypende beskrivelse"), blank=True, null=True)
    old_image = FileBrowseField(_("bilde"), max_length=200, directory=IMAGE_FOLDER,
                                extensions=IMAGE_EXTENSIONS, null=False, blank=False)
    image = models.ForeignKey(ResponsiveImage, null=True, blank=False, default=None)
    site = models.CharField(_("hjemmeside"), max_length=100)
    email_address = models.EmailField(_("epostaddresse"), max_length=75, blank=True, null=True)
    phone_number = models.CharField(_("telefonnummer"), max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    def images(self):
        if not self.old_image:
            return []
        from apps.companyprofile.utils import find_image_versions
        return find_image_versions(self)

    class Meta(object):
        verbose_name = _("Bedrift")
        verbose_name_plural = _("Bedrifter")
        permissions = (
            ('view_company', 'View Company'),
        )
