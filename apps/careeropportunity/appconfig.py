from django.apps import AppConfig


class CareeropportunityConfig(AppConfig):
    name = "apps.careeropportunity"
    verbose_name = "Careeropportunity"

    def ready(self):
        super().ready()

        from watson import search as watson
        from apps.careeropportunity.models import CareerOpportunity

        watson.register(
            CareerOpportunity,
            fields=(
                "title",
                "ingress",
                "description",
                "employment",
                "location",
                "company__name",
            ),
        )
