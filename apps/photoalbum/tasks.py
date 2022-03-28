import logging

from PIL import Image

try:
    from zappa.asynchronous import task
except ImportError:
    # Zappa is only required if we are running on Lambda
    def task(func):
        return func


from apps.gallery.util import ResponsiveImageHandler

from .models import Photo

logger = logging.getLogger(__name__)


@task
def create_responsive_photo_task(photo_id: int):
    photo = Photo.objects.get(pk=photo_id)
    raw_image = photo.raw_image

    pillow_image = Image.open(raw_image.image.path)
    image_width, image_height = pillow_image.size

    config = {
        "name": f"{photo}",
        "description": photo.description,
        "photographer": photo.photographer_name,
        "x": 0,
        "y": 0,
        "width": image_width,
        "height": image_height,
        "scaleX": 1,
        "scaleY": 1,
        "id": raw_image.id,
        "preset": "photoalbum",
    }

    responsive_image_handler = ResponsiveImageHandler(raw_image)
    status = responsive_image_handler.configure(config)
    if not status:
        logger.error(
            f"Fatal error when creating responsive image for photo {photo}, {status}"
        )

    status = responsive_image_handler.generate()
    if not status:
        logger.error(
            f"Fatal error when creating responsive image for photo {photo}, {status}"
        )

    if status and status.data:
        photo.refresh_from_db()
        photo.image = status.data
        photo.save()
