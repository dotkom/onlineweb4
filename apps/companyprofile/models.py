from django.db import models
from django.utils.translation import ugettext_lazy as _


class Company(models.Model):
    name = models.CharField(_(u"Bedriftsnavn"), max_length=100)
    # TODO Bilde
    short_description = models.TextField(_(u"Kort beskrivelse"), max_length=200)
    long_description = models.TextField(_(u"Utdypende beskrivelse"), blank=True, null=True)
    site = models.URLField(_(u"Hjemmeside"))
    email_address = models.EmailField(_(u"Epostaddresse"), max_length=75, blank=True, null=True)
    phone_number = models.IntegerField(_(u"Telefonnummer"), max_length=8, blank=True, null=True)
#   public_profile = models.BooleanField(_(u"Offentlig profil"), default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Bedrift")
        verbose_name_plural = _(u"Bedrifter")
