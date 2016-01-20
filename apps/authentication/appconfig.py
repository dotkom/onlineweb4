from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = 'apps.authentication'
    verbose_name = 'Authentication for OW4'

    def ready(self):
        super(AuthenticationConfig, self).ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.authentication.signals  # flake8: noqa
