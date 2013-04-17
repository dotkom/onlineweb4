# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from filebrowser.fields import FileBrowseField


class Article(models.Model):
    IMAGE_FOLDER = "images/article"
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']

    heading = models.CharField(_(u"tittel"), max_length=200)
    ingress = models.TextField(_(u"ingress"))
    content = models.TextField(_(u"content"))
    image_article = FileBrowseField(_(u"artikkel-bilde"),
        max_length=200, directory=IMAGE_FOLDER, blank=True,
        extensions=IMAGE_EXTENSIONS)
    image_thumbnail = FileBrowseField(_(u"thumbnail"),
        max_length=200, directory=IMAGE_FOLDER, blank=True,
        extensions=IMAGE_EXTENSIONS)
    image_featured = FileBrowseField(_(u"featured-bilde"),
        max_length=200, directory=IMAGE_FOLDER, blank=True,
        extensions=IMAGE_EXTENSIONS)
    created_date = models.DateTimeField(_(u"opprettet-dato"), auto_now_add=True, editable=False)
    changed_date = models.DateTimeField(_(u"sist endret"), editable=False, auto_now=True)
    published_date = models.DateTimeField(_(u"publisert"))

    created_by = models.ForeignKey(User, null=False, verbose_name=_(u"opprettet av"), related_name="created_by", editable=False)
    changed_by = models.ForeignKey(User, null=False, verbose_name=_(u"endret av"), related_name="changed_by", editable=False)
    featured = models.BooleanField(_(u"featured artikkel"), default=False)

    def __unicode__(self):
        return self.heading

    @property
    def tags(self):
        at = ArticleTag.objects.filter(article=self.id)
        tags = []
        for a in at:
            tags.append(a.tag)
        return tags

    @property
    def tagstring(self):
        tag_names = []
        for tag in self.tags:
            tag_names.append(tag.name)
        return u', '.join(tag_names)

    class Meta:
        verbose_name = _(u"artikkel")
        verbose_name_plural = _(u"artikler")
        ordering = ['published_date']


class Tag(models.Model):
    name = models.CharField(_(u"navn"), max_length=50)
    slug = models.CharField(_(u"kort navn"), max_length=30)

    @property
    def frequency(self):
        at = ArticleTag.objects.filter(tag=self.id)
        count = 0
        for a in at:
            count += 1
        return count

    def __unicode__(self):
        return self.name


class ArticleTag(models.Model):
    article = models.ForeignKey(Article, verbose_name=_(u"artikkel"))
    tag = models.ForeignKey(Tag, verbose_name=_(u"tag"))

    class Meta:
        verbose_name = _(u"tag")
        verbose_name_plural = _(u"tags")
