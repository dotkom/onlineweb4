from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = 'apps.notifications'
    verbose_name = 'Notifications'

    def ready(self):
        super().ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.notifications.signals  # noqa: F401
