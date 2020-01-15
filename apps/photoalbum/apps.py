from django.apps import AppConfig


class PhotoalbumConfig(AppConfig):
    name = "apps.photoalbum"
    verbose_name = "Fotoalbum"

    def ready(self):
        super().ready()
        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.photoalbum.signals  # noqa: F401

        from watson import search as watson

        from apps.photoalbum.models import Album, Photo, UserTag

        watson.register(
            Album,
            fields=(
                "title",
                "description",
                "created_by__first_name",
                "created_by__last_name",
                "created_by__username",
                "tags",
            ),
        )
        watson.register(
            Photo,
            fields=(
                "tags",
                "title",
                "description",
                "user_tags__user__first_name",
                "user_tags__user__last_name",
                "user_tags__user__username",
            ),
        )
        watson.register(
            UserTag, fields=("user__first_name", "user__last_name", "user__username")
        )
