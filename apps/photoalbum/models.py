# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from taggit.managers import TaggableManager
from unidecode import unidecode

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import BaseResponsiveImage

IMAGE_FOLDER = "images/photo_album"


class Album(models.Model):
    title = models.CharField(_("Tittel"), blank=False, null=False, max_length=50)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title

    @property
    def slug(self):
        return slugify(unidecode(self.title))


class Photo(BaseResponsiveImage):
    album = models.ForeignKey(
        to=Album,
        related_name='photos',
        on_delete=models.DO_NOTHING,
    )
    title = models.CharField('Tittel', max_length=200, null=True, blank=True)
    description = models.TextField('Beskrivelse', blank=True, default='', max_length=2048)
    tags = TaggableManager(help_text="En komma eller mellomrom-separert liste med tags.")

    photographer_name = models.CharField('Fotografnavn', max_length=100, null=False, blank=True)
    photographer = models.ForeignKey(
        to=User,
        related_name='uploaded_photos',
        verbose_name='Fotograf',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return self.title

    class Meta(BaseResponsiveImage.Meta):
        ordering = ('album', 'timestamp')


class UserTag(models.Model):
    """
    A tag identifying a user in a photo
    """
    user = models.ForeignKey(
        to=User,
        related_name='photo_tags',
        on_delete=models.CASCADE,
    )
    photo = models.ForeignKey(
        to=Photo,
        related_name='user_tags',
        on_delete=models.CASCADE,
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('photo', 'created_date', 'user',)
