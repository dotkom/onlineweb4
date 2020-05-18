from django.apps import AppConfig


class GalleryConfig(AppConfig):
    name = "apps.gallery"
    verbose_name = "Gallery"

    def ready(self):
        super(GalleryConfig, self).ready()

        from watson import search as watson

        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.gallery.signals  # noqa: F401
        from apps.gallery.models import ResponsiveImage

        # Perform checks that necessary directories exist on the disk
        from apps.gallery.util import verify_directory_structure

        verify_directory_structure()

        # Register the ResponsiveImage model for watson indexing
        watson.register(ResponsiveImage)
