from apps.companyprofile.models import Company
from rest_framework import serializers


class CompanySerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Company
        fields = ('name', 'site', 'images')
