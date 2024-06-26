from django.db import models
from django.db.models import SET_NULL

from apps.gallery.models import ResponsiveImage


class Resource(models.Model):
    title = models.CharField(max_length=35)
    description = models.TextField()
    image = models.ForeignKey(
        ResponsiveImage,
        related_name="resources",
        blank=True,
        null=True,
        on_delete=SET_NULL,
    )
    priority = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} (Priority: {self.priority})"

    class Meta:
        default_permissions = ("add", "change", "delete")
