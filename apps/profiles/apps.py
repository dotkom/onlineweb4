from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = "apps.profiles"
    verbose_name = "Profiles"

    def ready(self):
        super().ready()

        from reversion import revisions as reversion

        from apps.profiles.models import Privacy

        reversion.register(Privacy)
