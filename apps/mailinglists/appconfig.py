from django.apps import AppConfig


class MailinglistsConfig(AppConfig):
    name = "apps.mailinglists"
    verbose_name = "Mailinglists"

    def ready(self):
        super().ready()
        from watson import search as watson

        import apps.mailinglists.signals  # noqa: F401
        from apps.mailinglists.models import MailEntity, MailGroup

        watson.register(MailGroup)
        watson.register(MailEntity)
