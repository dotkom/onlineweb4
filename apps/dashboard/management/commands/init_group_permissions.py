from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = "Legger til korrekte tilganger til dashboardet i auth_permission med django-guardian."

    def handle_noargs(self, **options):
        print("TODO: Check if we actually need a management command.")
