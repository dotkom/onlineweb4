import logging

from django.db import models

from apps.authentication.models import OnlineUser as User
from apps.gallery.models import ResponsiveImage

from .constants import PermissionType

logger = logging.getLogger(__name__)


class Notification(models.Model):
    """
    Standard notification message which is sent to a single user on creation
    Closely modeled after the web notification spec:
    https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/showNotification
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
    from_email = models.EmailField(default="online@online.ntnu.no")

    image = models.ForeignKey(
        to=ResponsiveImage,
        related_name="notifications",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    title = models.CharField(max_length=100)
    body = models.TextField()
    # Tag can be null since the tag serves an an ID but only is present.
    # An empty string will result in all notifications without å specific tag being handled as the same notification.
    tag = models.CharField(max_length=100, null=True, blank=True)
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

    """
    Identifiers and keys used to send the push notification,
    as specified by https://w3c.github.io/push-api/#push-subscription
    """
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
        verbose_name = "Varselsabonnement"
        verbose_name_plural = "Varselsabonnementer"
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
        "Standardverdi for pushvarsel", default=False
    )

    def __str__(self):
        return self.permission_type

    class Meta:
        verbose_name = "Varseltillatelse"
        verbose_name_plural = "Varseltillatelser"
        ordering = ("permission_type",)


class UserPermission(models.Model):
    permission = models.ForeignKey(
        to=Permission, related_name="user_permissions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        to=User, related_name="user_notification_permissions", on_delete=models.CASCADE
    )
    allow_email = models.BooleanField(default=False)
    allow_push = models.BooleanField(default=False)

    @classmethod
    def create_all_for_user(cls, user: User):
        """
        Create permission settings for user if they don't all exists.
        """
        user_permissions_count = UserPermission.objects.filter(user=user).count()
        permission_count = Permission.objects.all().count()
        if user_permissions_count != permission_count:
            for permission in Permission.objects.all():
                user_permission, created = cls.objects.get_or_create(
                    permission=permission, user=user
                )
                if created:
                    user_permission.allow_email = permission.default_value_email
                    user_permission.allow_push = permission.default_value_push
                    user_permission.save()

    def __str__(self):
        return f"{self.permission} - {self.user}"

    class Meta:
        verbose_name = "Varseltillatelse for bruker"
        verbose_name_plural = "varseltillatelser for brukere"
        unique_together = (
            (
                "permission",
                "user",
            ),
        )
        ordering = ("permission", "user")
