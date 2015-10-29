import os

from base import MEDIA_ROOT

FILEBROWSER_MEDIA_ROOT = MEDIA_ROOT
FILEBROWSER_DIRECTORY = ''

FILEBROWSER_MAX_UPLOAD_SIZE = 52428800

# Versions

FILEBROWSER_VERSIONS = {

    # telling the user not to use resized pictures in the view (and avoid filebrowser crashing)
    'donotuse': {'verbose_name': 'CLICK SELECT INSTEAD, NO RESIZED PICTURES', 'width': 99, 'height': 99, 'opts': 'crop'},
    
    # thumbnail
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    
    # for articles
    'article_main': {'verbose_name': 'Artikkel hoved', 'width': 950, 'height': 534, 'opts': 'crop'},
    'article_full': {'verbose_name': 'Artikkel full', 'width': 1200, 'height': 444, 'opts': 'crop'},

    'article_front_featured': {'verbose_name': 'Artikkel forside featured', 'width': 584, 'height': 275, 'opts': 'crop'},
    'article_front_small': {'verbose_name': 'Artikkel forside lite', 'width': 174, 'height': 100, 'opts': 'crop'},
    'article_related': {'verbose_name': 'Artikkel related medium-small', 'width': 185, 'height': 70, 'opts': 'crop'},


    # Events
    'events_main' : {'verbose_name' : 'Event large', 'width': 584, 'height': 275, 'opts': 'crop'},
    'events_thumb' : {'verbose_name' : 'Event mini', 'width': 165, 'height': 71, 'opts': 'crop'},
    'events_archive' : {'verbose_name' : 'Event medium', 'width': 330, 'height': 142, 'opts': 'crop'},


    # Companies
    'companies_main' : {'verbose_name' : 'Company large', 'width': 584, 'height': 275, 'opts': 'crop'},
    'companies_thumb' : {'verbose_name' : 'Company mini', 'width': 165, 'height': 71, 'opts': 'crop'},
    'companies_medium' : {'verbose_name' : 'Company medium', 'width': 277, 'height': 146, 'opts': 'crop'},
    'companies_archive' : {'verbose_name' : 'Company medium', 'width': 330, 'height': 142, 'opts': 'crop'}
}

# define the thumbnail in the admin-view
FILEBROWSER_ADMIN_THUMBNAIL = 'admin_thumbnail'

# to avoid crashing and wrong resizes
FILEBROWSER_ADMIN_VERSIONS = ['donotuse']
