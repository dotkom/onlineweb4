from django.apps import AppConfig


class CompanyProfileConfig(AppConfig):
    name = "apps.companyprofile"
    verbose_name = "Companyprofile"

    def ready(self):
        super().ready()

        from watson import search as watson

        from apps.companyprofile.models import Company

        watson.register(
            Company,
            fields=(
                "name",
                "short_description",
                "long_description",
                "site",
                "email_address",
                "phone_number",
            ),
        )
