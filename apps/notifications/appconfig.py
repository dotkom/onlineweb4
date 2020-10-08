from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "apps.notifications"
    verbose_name = "Notifications"

    def ready(self):
        super().ready()

        import apps.notifications.signals  # noqa: F401
