# -*- coding: utf-8 -*-

from os import path
from PythonMagick import Image
from django.db import models
from django.db.models.signals import post_save
from filebrowser.fields import FileBrowseField


class Offline(models.Model):
    string = 'Introduksjonstekst'
    intro_text = models.TextField(string)

    def __unicode__(self):
        return self.string + ': Dette er teksten som vises over utgivelsene.'

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

    class Meta:
        verbose_name = 'Utgivelse'
        verbose_name_plural = 'Utgivelser'
        ordering = ['-release_date']


def resize(image, w, h):
    img = Image(image)  # copy
    s = "!%sx%s" % (w, h)
    img.scale(s)
    return img


def create_thumbnail(sender, instance=None, **kwargs):
    print 'Checking for thumbnail...'
    if instance is None:
        return
    t = Issue.objects.get(id=instance.id)
    url = str(t.issue).replace("/media/", "/var/websites/prod/onlineweb_uploads/")
    thumb = url + '.thumb.png'
    if path.exists(thumb) is False:
        print 'Thumbnail not found - creating...'
        im = Image(url + "[ 0]")
        height = 200  # Ønsket høyde på thumbnail
        width = height * float(float(im.size().width()) / float(im.size().height()))
        im = resize(im, width, height)
        im.write(thumb)
        print 'Thumbnail created, and is located at: %s' % (thumb)
    else:
        print 'Thumbnail already exists, and is located at: %s' % (thumb)

# FIXME: Denne kjører av en eller annen grunn to ganger
# Dette bør dog ikke være noe problem da jeg sjekker om det finnes en
# thumbnail fra før av før det genereres en ny.
post_save.connect(create_thumbnail, sender=Issue)
