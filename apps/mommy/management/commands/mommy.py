from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = "Starter mommy-sheduler"

    def handle_noargs(self, **options):
        from apps import mommy
        mommy.autodiscover()
        mommy.run(standalone=True)
