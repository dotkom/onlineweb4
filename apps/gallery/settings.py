# -*- coding: utf-8 -*-

import os

# Unhandled images
UNHANDLED_IMAGES_PATH = os.path.join("images", "non-edited")
UNHANDLED_THUMBNAIL_PATH = os.path.join(UNHANDLED_IMAGES_PATH, "thumbnails")
UNHANDLED_THUMBNAIL_SIZE = (200, 112)

# Responsive images
RESPONSIVE_IMAGES_PATH = os.path.join("images", "responsive")
RESPONSIVE_THUMBNAIL_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, "thumbnails")
RESPONSIVE_THUMBNAIL_SIZE = (200, 112)
RESPONSIVE_IMAGES_WIDE_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, "wide")
RESPONSIVE_IMAGES_LG_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, "lg")
RESPONSIVE_IMAGES_MD_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, "md")
RESPONSIVE_IMAGES_SM_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, "sm")
RESPONSIVE_IMAGES_XS_PATH = os.path.join(RESPONSIVE_IMAGES_PATH, "xs")

# Quality settings
THUMBNAIL_QUALITY = 70
RESPONSIVE_IMAGE_QUALITY = 100

# Presets and aspect ratios. Active presets are defined in the PRESETS list
ARTICLE = {
    "name": "article",
    "description": "Artikkel",
    "aspect_ratio": True,
    "aspect_ratio_x": 19,
    "aspect_ratio_y": 7,
    "min_width": 1280,
    "min_height": 474,
    "sizes": {"lg": (1280, 474), "md": (720, 405), "sm": (864, 486), "xs": (640, 360)},
}
COMPANY = {
    "name": "company",
    "description": "Bedriftslogo",
    "aspect_ratio": True,
    "aspect_ratio_x": 16,
    "aspect_ratio_y": 9,
    "min_width": 720,
    "min_height": 405,
    "sizes": {"lg": (720, 405), "md": (320, 180), "sm": (320, 180), "xs": (160, 90)},
}
EVENT = {
    "name": "event",
    "description": "Arrangement",
    "aspect_ratio": True,
    "aspect_ratio_x": 16,
    "aspect_ratio_y": 9,
    "min_width": 1280,
    "min_height": 720,
    "sizes": {"lg": (1280, 720), "md": (720, 405), "sm": (720, 405), "xs": (640, 360)},
}
OFFLINE = {
    "name": "offline",
    "description": "Offline",
    "aspect_ratio": True,
    "aspect_ratio_x": 1,
    "aspect_ratio_y": 1.28,
    "min_width": 1528,
    "min_height": 2160,
    "sizes": {
        "lg": (1688, 2160),
        "md": (844, 1080),
        "sm": (422, 540),
        "xs": (156, 200),
    },
}
PHOTOALBUM = {
    "name": "photoalbum",
    "description": "Fotoalbum",
    "aspect_ratio": False,
    "aspect_ratio_x": 4,
    "aspect_ratio_y": 3,
    "min_width": 200,
    "min_height": 150,
    "sizes": {
        "lg": (2400, 1800),
        "md": (1200, 900),
        "sm": (600, 450),
        "xs": (300, 225),
    },
}
PRODUCT = {
    "name": "product",
    "description": "Produktbilde",
    "aspect_ratio": True,
    "aspect_ratio_x": 5,
    "aspect_ratio_y": 6,
    "min_width": 520,
    "min_height": 624,
    "sizes": {"lg": (520, 624), "md": (520, 624), "sm": (390, 468), "xs": (260, 312)},
}

RESOURCE = {
    "name": "resource",
    "description": "Ressurs",
    "aspect_ratio": True,
    "aspect_ratio_x": 1,
    "aspect_ratio_y": 1,
    "min_width": 710,
    "min_height": 710,
    "sizes": {"lg": (710, 710), "md": (710, 710), "sm": (540, 540), "xs": (360, 360)},
}

# Keyword lookup
MODELS = {
    "article": ARTICLE,
    "event": EVENT,
    "company": COMPANY,
    "offline": OFFLINE,
    "product": PRODUCT,
    "resource": RESOURCE,
    "photoalbum": PHOTOALBUM,
}

# Active presets
PRESETS = [EVENT, ARTICLE, COMPANY, PRODUCT, RESOURCE, PHOTOALBUM]
