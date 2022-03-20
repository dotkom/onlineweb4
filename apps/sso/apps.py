from django.apps import AppConfig


class SsoConfig(AppConfig):
    name = "apps.sso"
    verbose_name = "Sso"

    def ready(self):
        # Is attached just by importations, thus ignored flake-rule
        from apps.sso.signals import handle_app_authorized  # noqa: F401
