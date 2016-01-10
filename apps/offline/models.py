# -*- coding: utf-8 -*-

import logging
from os import path
from subprocess import check_call, CalledProcessError
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from filebrowser.fields import FileBrowseField
from onlineweb4.settings.local import MEDIA_ROOT
from chunks.models import Chunk

import reversion

THUMBNAIL_HEIGHT = 200  # Ønsket høyde på thumbnail
IMAGE_FOLDER = "images/offline"


class ProxyChunk(Chunk):
    class Meta(object):
        proxy = True
        verbose_name = 'Informasjonstekst'
        verbose_name_plural = 'Informasjonstekster'


reversion.register(Chunk)


class Issue(models.Model):
    title = models.CharField(_(u"tittel"), max_length=50)
    release_date = models.DateField(_(u"utgivelsesdato"))
    description = models.TextField(_(u"beskrivelse"), blank=True, null=True)
    issue = FileBrowseField(_(u"pdf"), directory=IMAGE_FOLDER, max_length=500, extensions=['.pdf'])

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

    class Meta(object):
        verbose_name = 'Utgivelse'
        verbose_name_plural = 'Utgivelser'
        ordering = ['-release_date']
        permissions = (
            ('view_issue', 'View Issue'),
        )


reversion.register(Issue)


def create_thumbnail(sender, instance=None, **kwargs):
    logger = logging.getLogger(__name__)
    logger.debug('Checking for thumbnail...')
    if instance is None:
        return
    t = Issue.objects.get(id=instance.id)

    if t.thumbnail_exists is False:
        logger.debug('Thumbnail not found - creating...')

        # Fixes an annoying Exception in logs, not really needed
        # http://stackoverflow.com/questions/13193278/ {
        import threading
        threading._DummyThread._Thread__stop = lambda x: 42
        # }

        try:
            check_call(["convert", "-resize", "x" + str(THUMBNAIL_HEIGHT), t.url + "[0]", t.thumbnail])
        except (OSError, CalledProcessError) as e:
            logger.debug("ERROR: {0}".format(e))

        logger.debug('Thumbnail created, and is located at: %s' % t.thumbnail)

    else:
        logger.debug('Thumbnail already exists, and is located at: %s' % t.thumbnail)


post_save.connect(create_thumbnail, sender=Issue)
