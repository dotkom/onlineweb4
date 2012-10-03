# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from filebrowser.fields import FileBrowseField

class Article(models.Model):
    IMAGE_FOLDER = "/images/article"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

    heading = models.CharField(_("tittel"), max_length=200)
    ingress = models.TextField(_("ingress"))
    content = models.TextField(_("content"))
    image_article = FileBrowseField(_("artikkel-bilde"), 
        max_length=200, directory=IMAGE_FOLDER, blank=True,
        extensions=IMAGE_EXTENSIONS)
    image_thumbnail = FileBrowseField(_("thumbnail"),
        max_length=200, directory=IMAGE_FOLDER, blank=True,
        extensions=IMAGE_EXTENSIONS)
    image_featured = FileBrowseField(_("featured-bilde"),
        max_length=200, directory=IMAGE_FOLDER, blank=True,
        extensions=IMAGE_EXTENSIONS)
    created_date = models.DateTimeField(_("opprettet-dato"), auto_now_add=True, editable=False)
    changed_date = models.DateTimeField(_("sist endret"), editable=False)
    published_date = models.DateTimeField(_("publisert"))
    created_by = models.ForeignKey(User, verbose_name=_("opprettet av"), related_name="created_by", editable=False)
    changed_by = models.ForeignKey(User, verbose_name=_("endret av"), related_name="chneged_by", editable=False)
    featured = models.BooleanField(_("featured artikkel"), default=False)
    hurrdurr = models.BooleanField("blabla")

    class Meta:
        verbose_name = _("artikkel")
        verbose_name_plural = _("artikler")
        ordering = ['published_date']

class Tag(models.Model):
    name = models.CharField(_("navn"), max_length=50)
    slug = models.CharField(_("kort navn"), max_length=30)

class ArticleTag(models.Model):
    article = models.ForeignKey(Article, verbose_name=_("artikkel"))
    tag = models.ForeignKey(Tag, verbose_name=_("tag"))

    class Meta:
        unique_together = ("article", "tag",)
