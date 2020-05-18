from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = "apps.authentication"
    verbose_name = "Authentication for OW4"

    def ready(self):
        super(AuthenticationConfig, self).ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.authentication.signals  # noqa: F401

        from reversion import revisions as reversion
        from watson import search as watson

        from apps.authentication.models import OnlineUser, RegisterToken

        reversion.register(RegisterToken)
        watson.register(
            OnlineUser, fields=("first_name", "last_name", "ntnu_username", "nickname")
        )
