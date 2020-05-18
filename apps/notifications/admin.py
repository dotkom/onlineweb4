from django.contrib import admin

from apps.notifications import models


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    model = models.Notification
    list_display = (
        "recipient",
        "title",
        "created_date",
        "sent_email",
        "sent_push",
        "permission",
    )


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    model = models.Subscription
    list_display = (
        "user",
        "endpoint",
    )


@admin.register(models.Permission)
class PermissionSubscriptionAdmin(admin.ModelAdmin):
    model = models.Permission
    list_display = (
        "permission_type",
        "allow_email",
        "allow_push",
        "force_email",
        "force_push",
    )


@admin.register(models.UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    model = models.UserPermission
    list_display = (
        "permission",
        "user",
        "allow_email",
        "allow_push",
    )
