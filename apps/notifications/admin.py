from django.contrib import admin

from apps.notifications import models


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    model = models.Notification


@admin.register(models.NotificationSubscription)
class NotificationSubscriptionAdmin(admin.ModelAdmin):
    model = models.NotificationSubscription


@admin.register(models.NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    model = models.NotificationSetting
