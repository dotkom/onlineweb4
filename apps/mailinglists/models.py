from django.db import models
from django.utils.translation import ugettext as _


class Mailinglist(models.Model):
    email = models.EmailField(_("epostadresse"), unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    public = models.BooleanField(default=False)
    contained_emails = models.ManyToManyField(
        "self", blank=True, related_name="mailinglists_mail_is_in"
    )
