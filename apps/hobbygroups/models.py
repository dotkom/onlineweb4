from django.db import models
from apps.hobbygroups import settings


class Hobby(models.Model):
    title = models.CharField(max_length=25)
    description = models.TextField(max_length=250)
    image = models.ImageField(upload_to=settings.IMAGES_PATH)
    read_more_link = models.URLField(blank=True)

    def __str__(self):
        return self.title
