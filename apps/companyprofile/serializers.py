from rest_framework import serializers
from apps.companyprofile.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'site', 'images')