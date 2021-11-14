from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.disable_for_loaddata import disable_for_loaddata

from .models import MailEntity, MailGroup


@receiver(signal=post_save, sender=MailGroup)
@disable_for_loaddata
def create_organization_email_for_list(
    sender, instance: MailGroup, created: bool, **kwargs
):
    if created:
        MailEntity.objects.create(
            email=instance.email,
            name=instance.name,
            description=instance.description,
            public=instance.public,
        )
