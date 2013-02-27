import os

from base import MEDIA_ROOT

FILEBROWSER_MEDIA_ROOT = MEDIA_ROOT
FILEBROWSER_DIRECTORY = ''

# Versions

FILEBROWSER_VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},

    'article_main': {'verbose_name': 'Artikkel hoved', 'width': 950, 'height': '', 'opts': 'crop'},
    'article_front_featured': {'verbose_name': 'Artikkel forside featured', 'width': 584, 'height': 275, 'opts': 'crop'},
    'article_front_small': {'verbose_name': 'Artikkel forside lite', 'width': 174, 'height': 100, 'opts': 'crop'}
}

FILEBROWSER_ADMIN_VERSIONS = ['article_main', 'article_front_featured', 'article_front_small']

FILEBROWSER_ADMIN_THUMBNAIL = 'admin_thumbnail'
