from django.db import models

from apps.hobbygroups import settings


class Hobby(models.Model):
    title = models.CharField(max_length=25)
    description = models.TextField(max_length=250)
    image = models.ImageField(upload_to=settings.IMAGES_PATH)
    read_more_link = models.URLField(blank=True)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return "{title} (Priority: {priority})".format(title=self.title,
                                                       priority=self.priority)
