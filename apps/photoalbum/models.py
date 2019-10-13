# -*- coding: utf-8 -*-

from django.db import models, transaction
from django.template.defaultfilters import slugify
from django.utils import timezone
from taggit.managers import TaggableManager
from unidecode import unidecode

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage, UnhandledImage


class VisibleAlbumsManager(models.Manager):
    """
    Provides a queryset of just the albums visible to users
    """
    def get_queryset(self):
        return super().get_queryset().filter(published_date__lte=timezone.now())


class PublicAlbumsManager(VisibleAlbumsManager):
    """
    Provides a queryset of just the albums which are publicly available even without login
    """
    def get_queryset(self):
        return super().get_queryset().filter(public=True)


class Album(models.Model):
    # Managers
    objects = models.Manager()
    objects_visible = VisibleAlbumsManager()
    objects_public = PublicAlbumsManager()

    # Fields
    title = models.CharField('Tittel', blank=False, null=False, max_length=128, unique=True)
    description = models.TextField('Beskrivelse', blank=True, default='', max_length=2048)
    created_date = models.DateTimeField('Opprettelsesdato', auto_now_add=True)
    published_date = models.DateTimeField(
        verbose_name='Publiseringsdato',
        default=timezone.now,
        help_text='Når skal albumet bli synlig?',
    )
    tags = TaggableManager(help_text='En komma eller mellomrom-separert liste med tags.', blank=True)
    public = models.BooleanField(
        verbose_name='Synlig offentlig',
        default=False,
        help_text='Skal albumet være synlig for alle, selv uten innlogging?',
    )
    """ Keeps count of the photos in the album to create unique numbers """
    photo_counter = models.IntegerField(default=0, editable=False)

    created_by = models.ForeignKey(
        to=User,
        verbose_name='Oppretted av',
        related_name='created_albums',
        on_delete=models.DO_NOTHING,
    )

    @property
    def slug(self):
        return slugify(unidecode(self.title))

    @property
    def cover_photo(self):
        return self.photos.first()

    def increment_photo_counter(self) -> int:
        with transaction.atomic():
            self.refresh_from_db()
            self.photo_counter += 1
            self.save()
            return self.photo_counter

    def get_next_photo(self, photo: 'Photo') -> 'Photo':
        ordered_photos = self.photos.order_by('created_date')
        next_photo = ordered_photos.filter(created_date__gt=photo.created_date).first()
        return next_photo if next_photo else ordered_photos.first()

    def get_previous_photo(self, photo: 'Photo') -> 'Photo':
        ordered_photos = self.photos.order_by('-created_date')
        previous_photo = ordered_photos.filter(created_date__lt=photo.created_date).first()
        return previous_photo if previous_photo else ordered_photos.first()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Album'
        verbose_name_plural = 'Albumer'
        ordering = ('published_date', 'title',)


class Photo(models.Model):
    album = models.ForeignKey(
        to=Album,
        related_name='photos',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """ A relative id for the photo in an album, first photo will get '1', tenth in the album will get '10' """
    relative_id = models.IntegerField('Relativ id for album', null=False, blank=True, editable=False)
    """ Responsive image sources for the photo """
    image = models.ForeignKey(
        to=ResponsiveImage,
        related_name='album_photos',
        verbose_name='Bildefil',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """ Raw uploaded image. Set to null after responsive image is created """
    raw_image = models.ForeignKey(
        to=UnhandledImage,
        related_name='photo_uploads',
        verbose_name='Bildeopplastning',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_date = models.DateTimeField('Opprettelsesdato', auto_now_add=True)
    title = models.CharField('Tittel', max_length=200, null=False, blank=True)
    description = models.TextField('Beskrivelse', blank=True, default='', max_length=2048)
    tags = TaggableManager(help_text='En komma eller mellomrom-separert liste med tags.', blank=True)

    photographer_name = models.CharField('Fotografnavn', max_length=100, null=False, blank=True)
    photographer = models.ForeignKey(
        to=User,
        related_name='uploaded_photos',
        verbose_name='Fotograf',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('album', 'created_date')
        verbose_name = 'Bilde'
        verbose_name_plural = 'Bilder'
        unique_together = (('album', 'title',), ('album', 'relative_id',))


class UserTag(models.Model):
    """
    A tag identifying a user in a photo
    """
    user = models.ForeignKey(
        to=User,
        related_name='photo_tags',
        on_delete=models.CASCADE,
        verbose_name='Bruker',
    )
    photo = models.ForeignKey(
        to=Photo,
        related_name='user_tags',
        on_delete=models.CASCADE,
        verbose_name='Bilde',
    )
    created_date = models.DateTimeField('Opprettelsesdato', auto_now_add=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tagger'
        ordering = ('photo', 'created_date', 'user',)
        unique_together = (('user', 'photo',),)
