from django.db import models

from apps.authentication.models import OnlineUser as User
from apps.events.models import Event
from apps.notifications.dispatcher import NotificationDispatcher
from apps.notifications.handler import AbstractNotificationHandler


class EventRegistrationNotification(AbstractNotificationHandler):
    event = models.ForeignKey(
        to=Event,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    @staticmethod
    def signal(sender, instance: Event, created: bool, **kwargs):
        if instance.is_attendance_event():
            if created:
                EventRegistrationNotification.objects.create(event=instance)

            notification = EventRegistrationNotification.objects.get(event=instance)
            notification['dispatch_time'] = instance.attendance_event.registration_start
            notification.save()

    def gather_recipients(self) -> models.QuerySet[User]:
        """
        Gather users which should receive a notification about registration opening.
        :return: queryset of OnlineUser
        """

        """ All active users are eligible to receive registration permissions """
        queryset = User.objects.filter(is_active=True)
        return queryset

    def resolve_settings(self, users: models.QuerySet[User]) -> models.QuerySet[User]:
        permitted_users = users.filter(notification_settings__event_registration=True)
        return permitted_users

    def get_message_title(self, user: User, event: Event) -> str:
        return f'Påmeldingen til {event.title} åpner nå!'

    def get_message_body(self, user: User, event: Event) -> str:
        return None

    def get_message_url(self, user: User, event: Event):
        return event.get_absolute_url()

    def get_message_image_url(self, user: User, event: Event) -> str:
        """ If the event has one company, and is a bedpres or course; use company image """
        if len(event.company_event) == 1 and event.event_type in [2, 3]:
            return event.company_event[0].company.image.lg

        return event.image.lg

    def get_model_instance(self) -> Event:
        return self.event

    class Meta:
        tag = 'registration'
        dispatchers = [NotificationDispatcher]


models.signals.post_save(receiver=EventRegistrationNotification.signal, sender=Event)
