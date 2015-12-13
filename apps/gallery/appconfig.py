from django.apps import AppConfig


class GalleryConfig(AppConfig):
    name = 'apps.gallery'
    verbose_name = 'Gallery'

    def ready(self):
        super(GalleryConfig, self).ready()

        from watson import search as watson

        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.gallery.signals
        from apps.gallery.models import ResponsiveImage

        watson.register(ResponsiveImage)
