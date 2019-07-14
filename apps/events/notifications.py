from apps.events.models import CompanyEvent
from apps.gallery.models import ResponsiveImage
from apps.notifications.handler import AbstractNotificationHandler
from apps.notifications.types import NotificationType

from .models import Event


class EventUpdateNotification(AbstractNotificationHandler):
    message_type = NotificationType.EVENT_UPDATES

    def __init__(self, event: Event, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def get_tag(self, user) -> str:
        return f'{self.get_type()}-{self.event.id}'

    def get_title(self, user) -> str:
        return f'Arrangementet {self.event.title} har blitt oppdatert'

    def get_body(self, user) -> str:
        return (f'Det har skjedd endringer i arrangementet,\n'
                f'vennligst sjekk endringene og pass på at du fortsatt kan møte')

    def get_url(self, user) -> str:
        return self.event.get_absolute_url()

    def get_image(self, user) -> ResponsiveImage:
        if self.event.image is not None:
            return self.event.image

        if self.event.company_event.all().count() > 0:
            company_event: CompanyEvent = self.event.company_event.first()
            return company_event.company.image

        return None

    def get_recipients(self):
        if self.event.is_attendance_event():
            return [attendee.user for attendee in self.event.attendance_event.attendees.all()]
        super().get_recipients()
