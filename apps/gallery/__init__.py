# -*- coding: utf-8 -*-

from .util import verify_directory_structure


# We need to make sure that gallery can put files where needed
verify_directory_structure()

default_app_config = 'apps.gallery.appconfig.GalleryConfig'
