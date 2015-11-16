from django.apps import AppConfig

import reversion


class ProfilesConfig(AppConfig):
    name = 'apps.profiles'
    verbose_name = 'Profiles'

    def ready(self):
        super(ProfilesConfig, self).ready()

        from apps.profiles.models import Privacy

        reversion.register(Privacy)
