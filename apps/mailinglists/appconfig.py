from django.apps import AppConfig


class MailinglistsConfig(AppConfig):
    name = "apps.mailinglists"
    verbose_name = "Mailinglists"

    def ready(self):
        super().ready()
        # noinspection PyUnresolvedReferences
        import apps.mailinglists.signals  # noqa: F401
