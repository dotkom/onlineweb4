import logging

import requests
from django.conf import settings

VIMEO_API_TOKEN = settings.VIMEO_API_TOKEN
VIMEO_API_URL_BASE = "https://api.vimeo.com"
VIMEO_API_VIDEOS_URL = f"{VIMEO_API_URL_BASE}/videos"

logger = logging.getLogger(__name__)


def check_if_vimeo_video_exists(vimeo_id: str) -> bool:
    """
    Use Vimeo API to check if a video exists.
    The API returns a 200 OK if the video exists. 404 NOT_FOUND it it does not.
    """

    # Disable verification if no token is given
    if not VIMEO_API_TOKEN:
        logger.info("Vimeo API token not configured. Vimeo ID verification is disabled")
        return True

    video_url = f"{VIMEO_API_VIDEOS_URL}/{vimeo_id}"
    headers = {"Authorization": f"bearer {VIMEO_API_TOKEN}"}

    response = requests.get(url=video_url, headers=headers)

    return response.ok
