from django.utils import timezone
from rest_framework import serializers

from apps.companyprofile.models import Company
from apps.gallery.serializers import ResponsiveImageSerializer


class CompanySerializer(serializers.ModelSerializer):
    image = ResponsiveImageSerializer()
    event_count = serializers.SerializerMethodField()
    career_opportunity_count = serializers.SerializerMethodField()

    def get_event_count(self, company: Company):
        return company.events.filter(visible=True).count()

    def get_career_opportunity_count(self, company: Company):
        return company.career_opportunities.filter(start__lte=timezone.now()).count()

    class Meta:
        model = Company

        fields = (
            "id",
            "created_date",
            "name",
            "site",
            "image",
            "long_description",
            "short_description",
            "email_address",
            "phone_number",
            "event_count",
            "career_opportunity_count",
        )
