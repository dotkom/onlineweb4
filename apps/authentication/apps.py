from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = "apps.authentication"
    verbose_name = "Authentication for OW4"

    def ready(self):
        super().ready()

        from watson import search as watson

        import apps.authentication.schema  # noqa: F401
        import apps.authentication.signals  # noqa: F401
        from apps.authentication.models import OnlineUser

        watson.register(
            OnlineUser, fields=("first_name", "last_name", "ntnu_username", "nickname")
        )
