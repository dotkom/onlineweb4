# -*- coding: utf-8 -*-
import logging
from subprocess import CalledProcessError, check_call

from apps.offline.models import THUMBNAIL_HEIGHT


def create_thumbnail(instance):
    logger = logging.getLogger(__name__)
    logger.debug('Checking for thumbnail for "%s".' % instance.title)

    if instance.thumbnail_exists is False:
        logger.debug('Thumbnail for "%s" not found - creating...' % instance.title)

        # Fixes an annoying Exception in logs, not really needed
        # http://stackoverflow.com/questions/13193278/ {
        import threading
        threading._DummyThread._Thread__stop = lambda x: 42
        # }

        try:
            check_call(["convert", "-resize", "x" + str(THUMBNAIL_HEIGHT), instance.url + "[0]", instance.thumbnail])
        except (OSError, CalledProcessError) as e:
            logger.debug("ERROR: {0}".format(e))

        logger.debug('Thumbnail created, and is located at: %s' % instance.thumbnail)

    else:
        logger.debug('Thumbnail already exists, and is located at: %s' % instance.thumbnail)
