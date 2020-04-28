from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "apps.events"
    verbose_name = "Events"

    def ready(self):
        super(EventsConfig, self).ready()

        from watson import search as watson

        from apps.events.models import Event, Extras

        watson.register(Event)
        watson.register(Extras)
