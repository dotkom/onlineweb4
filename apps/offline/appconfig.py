from django.apps import AppConfig


class OfflineConfig(AppConfig):
    name = 'apps.offline'
    verbose_name = 'Offline'

    def ready(self):
        super(OfflineConfig, self).ready()

        from reversion import revisions as reversion

        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.offline.signals

        from chunks.models import Chunk
        from apps.offline.models import Issue

        reversion.register(Chunk)
        reversion.register(Issue)
