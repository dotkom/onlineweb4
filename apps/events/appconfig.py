from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = 'apps.events'
    verbose_name = 'Events'

    def ready(self):
        super().ready()

        # The following stops pycharm from nagging about unused import statement
        # noinspection PyUnresolvedReferences
        import apps.events.signals  # noqa: F401

        from watson import search as watson

        from apps.events.models import Event

        watson.register(Event)
