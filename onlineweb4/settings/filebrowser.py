import os

from base import MEDIA_ROOT

FILEBROWSER_MEDIA_ROOT = MEDIA_ROOT
FILEBROWSER_DIRECTORY = '' # becomes media root

# Versions
FILEBROWSER_VERSIONS = {
    'ad': {'verbose_name' : 'Ad (196px)', 'width': 196, 'height': '270', 'opts': 'crop'},
    'medium': {'verbose_name': 'Medium (460px)', 'width': 460, 'height': '', 'opts': ''},
    'small': {'verbose_name': 'Small (300px)', 'width': 300, 'height': '', 'opts': ''},
    'thumbnail': {'verbose_name': 'Thumbnail (140px)', 'width': 140, 'height': '', 'opts': ''},
}
FILEBROWSER_ADMIN_VERSIONS = ['small', 'thumbnail', 'ad', 'medium']
FILEBROWSER_ADMIN_THUMBNAIL = 'thumbnail'

#os.path.join(MEDIA_URL, 'filebrowser/')

