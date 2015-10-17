# -*- coding: utf-8 -*-

import logging
import os

from django.conf import settings as django_settings

# Log for potential directory creation
log = logging.getLogger(__name__)

# Unhandled images
UNHANDLED_IMAGES_PATH = os.path.join('images', 'non-edited')
UNHANDLED_THUMBNAIL_PATH = os.path.join(UNHANDLED_IMAGES_PATH, 'thumbnails')
UNHANDLED_THUMBNAIL_SIZE = (200, 112)


# Responsive images
RESPONSIVE_IMAGES_PATH = os.path.join('images', 'responsive')
RESPONSIVE_THUMBNAIL_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'thumbnails')
RESPONSIVE_THUMBNAIL_SIZE = (200, 112)
RESPONSIVE_IMAGES_WIDE_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'wide')
RESPONSIVE_IMAGES_WIDE_SIZE = (1280, 474)
RESPONSIVE_IMAGES_LG_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'lg')
RESPONSIVE_IMAGES_LG_SIZE = (1280, 720)
RESPONSIVE_IMAGES_MD_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'md')
RESPONSIVE_IMAGES_MD_SIZE = (1024, 576)
RESPONSIVE_IMAGES_SM_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'sm')
RESPONSIVE_IMAGES_SM_SIZE = (864, 486)
RESPONSIVE_IMAGES_XS_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, 'xs')
RESPONSIVE_IMAGES_XS_SIZE = (640, 360)

# Verify that the directories exist on current platform, create if not
if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_THUMBNAIL_PATH)):
    log.info('%s directory did not exist, creating it...' % RESPONSIVE_THUMBNAIL_PATH)
    os.makedirs(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_THUMBNAIL_PATH))
if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_XS_PATH)):
    log.info('%s directory did not exist, creating it...' % RESPONSIVE_IMAGES_XS_PATH)
    os.makedirs(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_XS_PATH))
if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_SM_PATH)):
    log.info('%s directory did not exist, creating it...' % RESPONSIVE_IMAGES_SM_PATH)
    os.makedirs(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_SM_PATH))
if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_MD_PATH)):
    log.info('%s directory did not exist, creating it...' % RESPONSIVE_IMAGES_MD_PATH)
    os.makedirs(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_MD_PATH))
if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_LG_PATH)):
    log.info('%s directory did not exist, creating it...' % RESPONSIVE_IMAGES_LG_PATH)
    os.makedirs(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_LG_PATH))
if not os.path.exists(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_WIDE_PATH)):
    log.info('%s directory did not exist, creating it...' % RESPONSIVE_IMAGES_WIDE_PATH)
    os.makedirs(os.path.join(django_settings.MEDIA_ROOT, RESPONSIVE_IMAGES_WIDE_PATH))
