from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = "apps.profiles"
    verbose_name = "Profiles"

    def ready(self):
        super().ready()

        from reversion import revisions as reversion

        from apps.profiles.models import Privacy

        from .signals import create_privacy_profile  # noqa

        reversion.register(Privacy)
