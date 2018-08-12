from django.db import models
from django.db.models import SET_NULL

from apps.gallery.models import ResponsiveImage


class Resource(models.Model):
    title = models.CharField(max_length=35)
    description = models.TextField()
    image = models.ForeignKey(ResponsiveImage, related_name='resources', blank=True, null=True, on_delete=SET_NULL)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return "{title} (Priority: {priority})".format(title=self.title, priority=self.priority)
