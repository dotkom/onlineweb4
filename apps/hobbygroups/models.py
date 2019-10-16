from django.db import models
from django.db.models import SET_NULL

from apps.gallery.models import ResponsiveImage


class Hobby(models.Model):
    title = models.CharField(max_length=25)
    description = models.TextField(max_length=300)
    image = models.ForeignKey(ResponsiveImage, related_name='hobbies', blank=True, null=True, on_delete=SET_NULL)
    read_more_link = models.URLField(blank=True)
    priority = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "{title} (Priority: {priority})".format(title=self.title,
                                                       priority=self.priority)

    class Meta:
        verbose_name_plural = "Hobbies"
        default_permissions = ('add', 'change', 'delete')
