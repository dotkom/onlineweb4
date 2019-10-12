from django.apps import AppConfig


class PhotoalbumConfig(AppConfig):
    name = 'apps.photoalbum'
    verbose_name = 'Fotoalbum'

    def ready(self):
        super().ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.photoalbum.signals  # noqa: F401
