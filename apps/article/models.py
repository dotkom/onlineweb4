# -*- coding: utf-8 -*-

import re
from unidecode import unidecode

from django.conf import settings
from django.db import models
from django.db.models import permalink, SET_NULL
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from taggit.managers import TaggableManager

from apps.gallery.models import ResponsiveImage

User = settings.AUTH_USER_MODEL


class Article(models.Model):
    IMAGE_FOLDER = "images/article"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

    heading = models.CharField(_(u"tittel"), max_length=45)
    ingress_short = models.CharField(_(u"kort ingress"), max_length=100)
    ingress = models.TextField(_(u"ingress"))
    content = models.TextField(_(u"content"))
    image = models.ForeignKey(ResponsiveImage, null=True, default=None, blank=True, on_delete=SET_NULL)
    video = models.CharField(_("vimeo id"), max_length=200, blank=True)
    created_date = models.DateTimeField(_(u"opprettet-dato"), auto_now_add=True, editable=False)
    changed_date = models.DateTimeField(_(u"sist endret"), editable=False, auto_now=True)
    published_date = models.DateTimeField(_(u"publisert"))

    created_by = models.ForeignKey(
        User, null=False,
        verbose_name=_(u"opprettet av"),
        related_name="created_by", editable=False
    )
    authors = models.CharField(_(u'forfatter(e)'), max_length=200, blank=True)
    changed_by = models.ForeignKey(
        User, null=False, verbose_name=_(u"endret av"), related_name="changed_by", editable=False
    )
    featured = models.BooleanField(_(u"featured artikkel"), default=False)

    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return self.heading

    def get_matchname(self):
        return re.findall(r"[0-9]+", self.video.lower())

    @property
    def slug(self):
        return slugify(unidecode(self.heading))

    @permalink
    def get_absolute_url(self):
        return 'article_details', None, {'article_id': self.id, 'article_slug': self.slug}

    class Meta(object):
        verbose_name = _(u"artikkel")
        verbose_name_plural = _(u"artikler")
        ordering = ['published_date']
        permissions = (
            ('view_article', 'View Article'),
        )
