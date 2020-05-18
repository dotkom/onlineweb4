from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Starter mommy-sheduler"

    def handle(self, **options):
        from apps import mommy

        mommy.autodiscover()
        mommy.run()
