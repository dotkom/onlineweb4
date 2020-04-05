from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Mail, Mailinglist


@receiver(signal=post_save, sender=Mailinglist)
def create_organization_email_for_list(
    sender, instance: Mailinglist, created: bool, **kwargs
):
    if created:
        Mail.objects.create(
            email=instance.email,
            name=instance.name,
            description=instance.description,
            public=instance.public,
        )
