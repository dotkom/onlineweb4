from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = 'apps.profiles'
    verbose_name = 'Profiles'

    def ready(self):
        super(ProfilesConfig, self).ready()
        from apps.profiles import signals