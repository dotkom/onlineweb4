import logging
from datetime import timedelta

from django.core.management import call_command

# from lego.apps.events.models import Event
# from lego.apps.files.models import File
# from lego.apps.files.storage import storage
# from lego.apps.users.fixtures.initial_abakus_groups import load_abakus_groups
# from lego.apps.users.fixtures.test_abakus_groups import load_test_abakus_groups
# from lego.apps.users.models import AbakusGroup, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.events.models import AttendanceEvent, Event

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Loads initial data from fixtures."
    verbosity = 0

    def add_arguments(self, parser):
        parser.add_argument(
            "--development",
            action="store_true",
            default=False,
            help="Load development fixtures.",
        )
        parser.add_argument(
            "--generate", action="store_true", default=False, help="Generate fixtures"
        )

    def call_command(self, *args, **options):
        call_command(*args, verbosity=self.verbosity, **options)

    def load_fixtures(self, fixtures):
        for fixture in fixtures:
            path = "apps/{}".format(fixture)
            self.call_command("loaddata", path)

    def handle(self, *args, **options):
        log.info("Loading regular fixtures:")
        log.info("Loading development fixtures:")
        self.load_fixtures(["authentication/fixtures/development_users.yaml"])
        self.load_fixtures(["events/fixtures/development_events.yaml"])
        self.load_fixtures(
            [
                # "users/fixtures/development_users.yaml",
                # "users/fixtures/development_memberships.yaml",
                # "companies/fixtures/development_companies.yaml",
                # "events/fixtures/development_events.yaml",
                # "events/fixtures/development_pools.yaml",
                # "events/fixtures/development_registrations.yaml",
                # "articles/fixtures/development_articles.yaml",
                # "quotes/fixtures/development_quotes.yaml",
                # "podcasts/fixtures/development_podcasts.yaml",
                # "polls/fixtures/development_polls.yaml",
                # "oauth/fixtures/development_applications.yaml",
                # "reactions/fixtures/development_reactions.yaml",
                # "joblistings/fixtures/development_joblistings.yaml",
                # "surveys/fixtures/development_surveys.yaml",
                # "users/fixtures/development_photo_consents.yaml",
            ]
        )

        self.update_event_dates()

        log.info("Done!")

    def update_event_dates(self):
        date = timezone.now().replace(hour=16, minute=15, second=0, microsecond=0)
        for i, event in enumerate(Event.objects.all()):
            event.event_start = date + timedelta(days=i + 10)
            event.event_end = date + timedelta(days=i + 10, hours=4)

            event.save()

            try:
                attendance_event = AttendanceEvent.objects.get(event=event)
                # registration time one day ago
                attendance_event.registration_start = timezone.now() - timedelta(days=1)
                attendance_event.registration_end = event.event_start - timedelta(
                    days=1
                )
                attendance_event.unattend_deadline = event.event_start - timedelta(
                    days=0.5
                )
                attendance_event.save()
            except AttendanceEvent.DoesNotExist:
                log.warning(f"No AttendanceEvent found for Event ID {event.id}")
