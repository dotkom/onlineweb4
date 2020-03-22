from django.db.models.signals import post_init
from django.dispatch import receiver

from .models import Mail, Mailinglist


@receiver(signal=post_init, sender=Mailinglist)
def create_organization_email_for_list(sender, instance: Mailinglist, **kwargs):
    Mail.objects.create(
        email=instance.email,
        name=instance.name,
        description=instance.description,
        public=instance.public,
    )
