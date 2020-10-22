from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MailEntity, MailGroup


@receiver(signal=post_save, sender=MailGroup)
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
