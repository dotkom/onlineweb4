from django.apps import AppConfig

import watson


class EventsConfig(AppConfig):
    name = 'apps.events'
    verbose_name = 'Events'

    def ready(self):
        super(EventsConfig, self).ready()

        from apps.events.models import Event

        watson.register(Event)
