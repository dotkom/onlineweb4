from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from apps.profiles.models import Privacy
from utils.disable_for_loaddata import disable_for_loaddata

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
@disable_for_loaddata
def create_privacy_profile(**kwargs):
    instance = kwargs.get("instance")
    created = kwargs.get("created")

    if created:
        Privacy.objects.get_or_create(user=instance)
