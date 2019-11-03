from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer

from apps.careeropportunity.models import CareerOpportunity
from apps.companyprofile.serializers import CompanySerializer


class LocationTagListSerializerFieldWithSlug(serializers.ModelSerializer):
    def to_representation(self, obj):
        locations = []
        for tag in obj.all():
            locations.append({"name": tag.name, "slug": tag.slug})

        return locations


class CareerSerializer(TaggitSerializer, serializers.ModelSerializer):
    company = CompanySerializer()
    employment = serializers.SerializerMethodField()
    location = LocationTagListSerializerFieldWithSlug()

    class Meta:
        model = CareerOpportunity
        fields = (
            "id",
            "company",
            "title",
            "ingress",
            "description",
            "application_link",
            "start",
            "end",
            "featured",
            "deadline",
            "employment",
            "location",
        )

    def get_employment(self, obj):
        return {"id": obj.employment, "name": obj.get_employment_display()}
