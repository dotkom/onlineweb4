from django.apps import AppConfig


class GsuiteConfig(AppConfig):
    name = "apps.gsuite"
    verbose_name = "G Suite Utilities"

    def ready(self):
        super().ready()

        import apps.gsuite.mail_syncer.signals  # noqa: F401
