from django.db import models
from django.utils.translation import gettext as _


class Company(models.Model):
    company_name = models.CharField(_('company name'),
            max_length=100,
            primary_key=True)

    description = models.TextField("beskrivelse")
    url = models.URLField()
    # TODO: image
