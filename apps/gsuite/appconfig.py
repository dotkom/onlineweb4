from django.apps import AppConfig


class GsuiteConfig(AppConfig):
    name = 'apps.gsuite'
    verbose_name = 'G Suite Utilities'

    def ready(self):
        super(GsuiteConfig, self).ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.gsuite.mail_syncer.signals  # noqa: F401
