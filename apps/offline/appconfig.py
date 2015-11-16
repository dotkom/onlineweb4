from django.apps import AppConfig

import reversion


class OfflineConfig(AppConfig):
    name = 'apps.offline'
    verbose_name = 'Offline'

    def ready(self):
        super(OfflineConfig, self).ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.offline.signals

        from chunks.models import Chunk
        from apps.offline.models import Issue

        reversion.register(Chunk)
        reversion.register(Issue)
