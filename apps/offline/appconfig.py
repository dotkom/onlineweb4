from django.apps import AppConfig


class OfflineConfig(AppConfig):
    name = "apps.offline"
    verbose_name = "Offline"

    def ready(self):
        super(OfflineConfig, self).ready()

        from chunks.models import Chunk
        from reversion import revisions as reversion

        import apps.offline.signals  # noqa: F401
        from apps.offline.models import Issue  # noqa: F401

        reversion.register(Chunk)
