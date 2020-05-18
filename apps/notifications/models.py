import logging

from django.conf import settings
from django.db import models

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage

from .constants import DEFAULT_NOTIFICATION_ICON_URL, PermissionType

logger = logging.getLogger(__name__)


class Notification(models.Model):
    """
    Standard notification message which is sent to a single user on creation
    """

    recipient = models.ForeignKey(
        to=User,
        verbose_name="Mottaker",
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    created_date = models.DateTimeField(auto_now_add=True)
    sent_email = models.BooleanField(default=False)
    sent_push = models.BooleanField(default=False)
    permission = models.ForeignKey(
        to="Permission", related_name="notifications", on_delete=models.DO_NOTHING
    )
    from_mail = models.EmailField(default=settings.DEFAULT_FROM_EMAIL)

    """ Icon can be overridden, but should probably not be in most cases """
    icon = models.URLField(
        max_length=1024, default=DEFAULT_NOTIFICATION_ICON_URL, blank=True,
    )
    image = models.ForeignKey(
        to=ResponsiveImage,
        related_name="notifications",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    title = models.CharField(max_length=60)
    body = models.CharField(max_length=512)
    tag = models.CharField(max_length=50, null=True, blank=True)
    url = models.CharField(max_length=1024, default="/", blank=True)

    require_interaction = models.BooleanField(default=False)
    renotify = models.BooleanField(default=False)
    silent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.recipient}"

    class Meta:
        verbose_name = "Varsel"
        verbose_name_plural = "Varsler"
        ordering = (
            "created_date",
            "recipient",
            "title",
        )


class Subscription(models.Model):
    """
    Model describing a webpush notification subscription.
    """

    user = models.ForeignKey(
        to=User, related_name="notification_subscriptions", on_delete=models.CASCADE
    )

    """ Identifiers and keys used to send the push notification. Can be really damned long """
    endpoint = models.URLField(unique=True, max_length=500)
    auth = models.CharField(unique=True, max_length=500)
    p256dh = models.CharField(unique=True, max_length=500)

    def to_vapid_format(self):
        subscription_info = {
            "endpoint": self.endpoint,
            "keys": {"auth": self.auth, "p256dh": self.p256dh},
        }
        return subscription_info

    def __str__(self):
        return f"{self.user} - {self.endpoint}"

    class Meta:
        verbose_name = "Varselsabbonement"
        verbose_name_plural = "Varselsabbonementer"
        ordering = (
            "user",
            "endpoint",
        )
        unique_together = (("user", "endpoint"),)


class Permission(models.Model):
    permission_type = models.CharField(
        "Type", max_length=128, choices=PermissionType.choices, unique=True
    )
    users = models.ManyToManyField(
        to=User, through="UserPermission", related_name="notification_permissions"
    )
    # Override user permission for specific sending methods.
    force_email = models.BooleanField("Tving e-post", default=False)
    force_push = models.BooleanField("Tving pushvarsel", default=False)

    # Allow or disallow specific sending methods for this permission type.
    allow_email = models.BooleanField("Tillat e-post", default=True)
    allow_push = models.BooleanField("Tillat pushvarsel", default=True)

    # Default values permissions types
    default_value_email = models.BooleanField("Standardverdi for e-post", default=False)
    default_value_push = models.BooleanField(
        "Standardverdi fro pushvarsel", default=False
    )

    def __str__(self):
        return self.permission_type

    class Meta:
        verbose_name = "Varseltillatelse"
        verbose_name_plural = "Varseltillatelser"
        ordering = ("permission_type",)


class UserPermission(models.Model):
    permission = models.ForeignKey(
        to=Permission, related_name="user_permission", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        to=User, related_name="user_notification_permissions", on_delete=models.CASCADE
    )
    allow_email = models.BooleanField(default=False)
    allow_push = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.permission} - {self.user}"

    class Meta:
        verbose_name = "Varseltillatelse for bruker"
        verbose_name_plural = "varseltillatelser for brukere"
        unique_together = (("permission", "user",),)
        ordering = ("permission", "user")
