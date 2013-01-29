# -*- coding: utf-8 -*-

from os import path
from subprocess import check_call, CalledProcessError
from django.db import models
from django.db.models.signals import post_save
from filebrowser.fields import FileBrowseField
from onlineweb4.settings.local import MEDIA_ROOT


class Offline(models.Model):
    string = 'Introduksjonstekst'
    intro_text = models.TextField(string)

    def __unicode__(self):
        return self.string + ': Dette er teksten som vises over utgivelsene.'

    @property
    def issues(self):
        return Issue.objects.all()

    class Meta:
        verbose_name = 'Introduksjonstekst'
        verbose_name_plural = verbose_name


class Issue(models.Model):
    IMAGE_FOLDER = "images/offline"

    title = models.CharField("tittel", max_length=50)
    release_date = models.DateField("utgivelsesdato")
    description = models.TextField("beskrivelse", blank=True, null=True)
    issue = FileBrowseField("pdf", directory=IMAGE_FOLDER, max_length=500, extensions=['.pdf'])

    def release_date_to_string(self):
        month = {
            1: "Januar",
            2: "Februar",
            3: "Mars",
            4: "April",
            5: "Mai",
            6: "Juni",
            7: "Juli",
            8: "August",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember"
        }
        return month[self.release_date.month]

    def __unicode__(self):
        return self.title

    @property
    def url(self):
        # TODO: url kan være feil ved prodsetting
        url = str(self.issue).replace("/media/", "/var/websites/prod/onlineweb_uploads/")
        url = path.join(MEDIA_ROOT, url)
        return url

    @property
    def thumbnail(self):
        thumb = self.url + '.thumb.png'
        return thumb

    @property
    def thumbnail_exists(self):
        return path.exists(self.thumbnail)

    class Meta:
        verbose_name = 'Utgivelse'
        verbose_name_plural = 'Utgivelser'
        ordering = ['-release_date']


def create_thumbnail(sender, instance=None, **kwargs):
    print 'Checking for thumbnail...'
    if instance is None:
        return
    t = Issue.objects.get(id=instance.id)

    if t.thumbnail_exists is False:
        print 'Thumbnail not found - creating...'

        try:
            height = 200  # Ønsket høyde på thumbnail
            check_call(["convert", "-resize", "x"+str(height), t.url+"[0]", t.thumbnail])
        except (OSError, CalledProcessError) as e:
            print("ERROR: {0}".format(e))

        print 'Thumbnail created, and is located at: %s' % (t.thumbnail)

    else:
        print 'Thumbnail already exists, and is located at: %s' % (t.thumbnail)


post_save.connect(create_thumbnail, sender=Issue)
