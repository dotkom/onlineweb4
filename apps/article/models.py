# -*- coding: utf-8 -*-

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import SET_NULL
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import ugettext as _
from taggit.managers import TaggableManager
from unidecode import unidecode

from apps.gallery.models import ResponsiveImage

from .tasks import check_if_vimeo_video_exists

User = settings.AUTH_USER_MODEL


def vimeo_id_validator(vimeo_id: str):
    if not check_if_vimeo_video_exists(vimeo_id):
        raise ValidationError(_('Vimeo videoen existerer ikke'))


class Article(models.Model):
    IMAGE_FOLDER = "images/article"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

    heading = models.CharField(_("tittel"), max_length=45)
    ingress_short = models.CharField(_("kort ingress"), max_length=100)
    ingress = models.TextField(_("ingress"))
    content = models.TextField(_("content"))
    image = models.ForeignKey(ResponsiveImage, null=True, default=None, blank=True, on_delete=SET_NULL)
    video = models.CharField(_("vimeo id"), max_length=200, blank=True, validators=[vimeo_id_validator])
    created_date = models.DateTimeField(_("opprettet-dato"), auto_now_add=True, editable=False)
    changed_date = models.DateTimeField(_("sist endret"), editable=False, auto_now=True)
    published_date = models.DateTimeField(_("publisert"))

    created_by = models.ForeignKey(
        User, null=False,
        verbose_name=_("opprettet av"),
        related_name="created_by",
        editable=False,
        on_delete=models.CASCADE
    )
    authors = models.CharField(_('forfatter(e)'), max_length=200, blank=True)
    changed_by = models.ForeignKey(
        User, null=False,
        verbose_name=_("endret av"),
        related_name="changed_by",
        editable=False,
        on_delete=models.CASCADE
    )
    featured = models.BooleanField(_("featured artikkel"), default=False)

    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.heading

    def get_matchname(self):
        return re.findall(r"[0-9]+", self.video.lower())

    @property
    def slug(self):
        return slugify(unidecode(self.heading))

    def get_absolute_url(self):
        return reverse('article_details', kwargs={'article_id': self.id, 'article_slug': self.slug})

    class Meta:
        verbose_name = _("artikkel")
        verbose_name_plural = _("artikler")
        ordering = ['published_date']
        permissions = (
            ('view_article', 'View Article'),
        )
        default_permissions = ('add', 'change', 'delete')
