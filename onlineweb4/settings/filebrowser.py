import os
from base import MEDIA_ROOT

FILEBROWSER_MEDIA_ROOT = MEDIA_ROOT
FILEBROWSER_DIRECTORY = '' # becomes media root

# Versions
FILEBROWSER_VERSIONS = {
    # telling the user not to use resized pictures in the view (and avoid filebrowser crashing)
    'donotuse': {'verbose_name': 'CLICK SELECT INSTEAD, NO RESIZED PICTURES', 'width': 99, 'height': 99, 'opts': 'crop'},
    
    # thumbnail
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    
    # for articles
    'article_main': {'verbose_name': 'Artikkel hoved', 'width': 950, 'height': 534, 'opts': 'crop'},
    'article_front_featured': {'verbose_name': 'Artikkel forside featured', 'width': 584, 'height': 275, 'opts': 'crop'},
    'article_front_small': {'verbose_name': 'Artikkel forside lite', 'width': 174, 'height': 100, 'opts': 'crop'}
}

# define the thumbnail in the admin-view
FILEBROWSER_ADMIN_THUMBNAIL = 'admin_thumbnail'

# to avoid crashing and wrong resizes
FILEBROWSER_ADMIN_VERSIONS = ['donotuse']