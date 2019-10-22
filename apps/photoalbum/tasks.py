import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from onlineweb4.celery import app
from PIL import Image

from apps.authentication.models import OnlineUser as User
from apps.gallery.util import ResponsiveImageHandler

from .models import Photo

logger = logging.getLogger(__name__)


def send_report_on_photo(user: User, photo: Photo, description: str):
    to_emails = [settings.EMAIL_PROKOM]
    content = f'Bruker {user.get_full_name()} har rapportert bilde %s med begrunnelse {description}'

    try:
        EmailMessage("[Rapportering av bilde]", content, settings.DEFAULT_FROM_EMAIL, to_emails).send()
    except ImproperlyConfigured:
        logger.warning(f'Failed to send the report of the photo to prokom from user {user} on photo #{photo}.')


@app.task(bind=True)
def create_responsive_photo_task(self, photo_id: int):
    photo = Photo.objects.get(pk=photo_id)
    raw_image = photo.raw_image

    pillow_image = Image.open(raw_image.image.path)
    image_width, image_height = pillow_image.size

    config = {
        'name': f'{photo}',
        'description': photo.description,
        'photographer': photo.photographer_name,
        'x': 0,
        'y': 0,
        'width': image_width,
        'height': image_height,
        'scaleX': 1,
        'scaleY': 1,
        'id': raw_image.id,
        'preset': 'photoalbum',
    }

    responsive_image_handler = ResponsiveImageHandler(raw_image)
    status = responsive_image_handler.configure(config)
    if not status:
        logger.error(f'Fatal error when creating responsive image for photo {photo}, {status}')

    status = responsive_image_handler.generate()
    if not status:
        logger.error(f'Fatal error when creating responsive image for photo {photo}, {status}')

    if status and status.data:
        photo.refresh_from_db()
        photo.image = status.data
        photo.save()
