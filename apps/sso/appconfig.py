from django.apps import AppConfig


class SsoConfig(AppConfig):
    name = "apps.sso"
    verbose_name = "Sso"

    def ready(self):
        from apps.sso.signals import handle_app_authorized
