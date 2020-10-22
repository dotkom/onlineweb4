from django.apps import AppConfig


class WebshopConfig(AppConfig):
    name = "apps.webshop"
    verbose_name = "Online Webshop"

    def ready(self):
        super().ready()

        import apps.webshop.signals  # noqa: F401
