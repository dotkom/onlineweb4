from django.db import models
from django.utils.translation import ugettext_lazy as _

from filebrowser.fields import FileBrowseField

import reversion

from apps.gallery.models import ResponsiveImage


class Company(models.Model):

    IMAGE_FOLDER = "images/companies"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

    name = models.CharField(_(u"bedriftsnavn"), max_length=100)
    short_description = models.TextField(_(u"kort beskrivelse"), max_length=200)
    long_description = models.TextField(_(u"utdypende beskrivelse"), blank=True, null=True)
    old_image = FileBrowseField(_(u"bilde"), max_length=200, directory=IMAGE_FOLDER,
                                extensions=IMAGE_EXTENSIONS, null=False, blank=False)
    image = models.ForeignKey(ResponsiveImage, null=True, blank=False, default=None)
    site = models.CharField(_(u"hjemmeside"), max_length=100)
    email_address = models.EmailField(_(u"epostaddresse"), max_length=75, blank=True, null=True)
    phone_number = models.CharField(_(u"telefonnummer"), max_length=20, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def images(self):
        if not self.old_image:
            return []
        from apps.companyprofile.utils import find_image_versions
        return find_image_versions(self)

    class Meta(object):
        verbose_name = _(u"Bedrift")
        verbose_name_plural = _(u"Bedrifter")
        permissions = (
            ('view_company', 'View Company'),
        )

reversion.register(Company)
