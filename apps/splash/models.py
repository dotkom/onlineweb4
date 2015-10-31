from django.db import models

from django_extensions.db.models import TimeStampedModel
import datetime
import reversion


class SplashYearManager(models.Manager):
    def current(self):
        # I'm really sorry ...
        return self.get(start_date__gt=str(datetime.date.today() - datetime.timedelta(180)))


class SplashYear(models.Model):
    title = models.CharField(u'title', max_length=100)
    start_date = models.DateField(u'start_date')

    objects = SplashYearManager()

    def __unicode__(self):
        return self.title

    class Meta(object):
        ordering = ('-start_date',)


class SplashEvent(TimeStampedModel, models.Model):
    title = models.CharField(u'title', max_length=100)
    content = models.TextField(u'content')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    splash_year = models.ForeignKey('SplashYear', related_name='splash_events')

    def __unicode__(self):
        return self.title

    class Meta(object):
        ordering = ('start_time',)

reversion.register(SplashYear)
reversion.register(SplashEvent)
