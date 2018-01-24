from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from apps.events.models import Event
from apps.events.utils import get_organizer_by_event_type


def traverse_relations(event):
    # Check if this is an attendance event, and if so, save it.
    if hasattr(event, 'attendance_event'):
        event.attendance_event.save()

        if hasattr(event, 'companies'):
            for company_event in event.companies.all():
                company_event.save()

        # Save all attendees too
        for attendee in event.attendance_event.attendees.all():
            attendee.save()

        # Check if the event has any reservations, and if so, save it.
        if hasattr(event.attendance_event, 'reserved_seats'):
            event.attendance_event.reserved_seats.save()

            # Save all reservees as too
            for reservee in event.attendance_event.reserved_seats.reservees.all():
                reservee.save()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--all', help='Save all event-related objects as well',
                            default=False, dest='save_all', action='store_true')
        parser.add_argument('--debug', help='Show which events are saved. Errors will be printed even with this off.',
                            default=False, dest='print_debug', action='store_true')

    def handle(self, *args, **options):
        save_all = options.get('save_all', False)

        print('Will {}save all objects related to each event.'.format('' if save_all else '*not* '))

        for event in Event.objects.all():
            if options.get('print_debug', False):
                print('Triggering save for "{}"'.format(event.title))

            organizer_obj = get_organizer_by_event_type(event.event_type)
            if not organizer_obj:
                print('Could not get organizer for "{}" (#{})'.format(event.title, event.pk))
                continue

            event.organizer = Group.objects.get(id=organizer_obj.id)
            event.save()

            # If set, run overridden .save() for related objects as well.
            if save_all:
                traverse_relations(event)
