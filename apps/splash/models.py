from django.db import models


class SplashEvent(models.Model):
    title = models.CharField('title', max_length=100)
    content = models.TextField('content')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta(object):
        ordering = ('start_time',)
        default_permissions = ('add', 'change', 'delete')
