from django.db import models

from apps.resourcecenter import settings


class Resource(models.Model):
    title = models.CharField(max_length=35)
    description = models.TextField()
    image = models.ImageField(upload_to=settings.IMAGES_PATH)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return "{title} (Priority: {priority})".format(title=self.title,
                                                       priority=self.priority)
