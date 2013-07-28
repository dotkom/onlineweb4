from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.userprofile.models import FIELD_OF_STUDY_CHOICES
from filebrowser.fields import FileBrowseField

class Company(models.Model):

    IMAGE_FOLDER = "images/companies"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']


    name = models.CharField(_(u"bedriftsnavn"), max_length=100)
    short_description = models.TextField(_(u"kort beskrivelse"), max_length=200)
    long_description = models.TextField(_(u"utdypende beskrivelse"), blank=True, null=True)
    image = FileBrowseField(_(u"bilde"), 
        max_length=200, directory=IMAGE_FOLDER,
        extensions=IMAGE_EXTENSIONS, null=False, blank=False)
    site = models.URLField(_(u"hjemmeside"))
    email_address = models.EmailField(_(u"epostaddresse"), max_length=75, blank=True, null=True)
    phone_number = models.IntegerField(_(u"telefonnummer"), max_length=8, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Bedrift")
        verbose_name_plural = _(u"Bedrifter")
