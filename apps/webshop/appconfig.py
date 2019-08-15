from django.apps import AppConfig


class WebshopConfig(AppConfig):
    name = 'apps.webshop'
    verbose_name = 'Online Webshop'

    def ready(self):
        super().ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.webshop.signals  # noqa: F401
