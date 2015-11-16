from django.apps import AppConfig

import reversion
import watson


class AuthenticationConfig(AppConfig):
    name = 'apps.authentication'
    verbose_name = 'Authentication for OW4'

    def ready(self):
        super(AuthenticationConfig, self).ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.authentication.signals  # flake8: noqa

        from apps.authentication.models import OnlineUser, RegisterToken

        reversion.register(RegisterToken)
        watson.register(OnlineUser, fields=('first_name', 'last_name', 'ntnu_username', 'nickname'))

        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.authentication.signals
