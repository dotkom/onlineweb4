from django.db import models
from django.utils.translation import gettext as _


class Extras(models.Model):
    """
    Choices for events
    """

    choice = models.CharField("valg", max_length=69)
    note = models.CharField("notat", max_length=200, blank=True, null=True)

    def __str__(self):
        return self.choice

    class Meta:
        verbose_name = _("ekstra valg")
        verbose_name_plural = _("ekstra valg")
        ordering = ["choice"]
        default_permissions = ("add", "change", "delete")
