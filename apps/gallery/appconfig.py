from django.apps import AppConfig

import watson


class GalleryConfig(AppConfig):
    name = 'apps.gallery'
    verbose_name = 'Gallery'

    def ready(self):
        super(GalleryConfig, self).ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.gallery.signals
        from apps.gallery.models import ResponsiveImage

        watson.register(ResponsiveImage)
