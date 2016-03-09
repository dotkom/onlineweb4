# -*- coding: utf-8 -*-

import os

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

# Quality settings
THUMBNAIL_QUALITY = 70
RESPONSIVE_IMAGE_QUALITY = 100

# Presets and aspect ratios
ARTICLE = {
    'aspect_ratio': True,
    'aspect_ratio_x': 19,
    'aspect_ratio_y': 7,
    'min_width': 1280,
    'min_height': 720
}
COMPANY = {
    'aspect_ratio': True,
    'aspect_ratio_x': 16,
    'aspect_ratio_y': 9,
    'min_width': 360,
    'min_height': 170,
}
EVENT = {
    'aspect_ratio': True,
    'aspect_ratio_x': 16,
    'aspect_ratio_y': 9,
    'min_width': 1280,
    'min_height': 720
}
OFFLINE = {
    'aspect_ratio': False,
    'aspect_ratio_x': 1,
    'aspect_ratio_y': 1.414,
    'min_width': 480,
    'min_height': 640
}
PRODUCT = {
    'aspect_ratio': True,
    'aspect_ratio_x': 5,
    'aspect_ratio_y': 6,
    'min_width': 128,
    'min_height': 128
}
