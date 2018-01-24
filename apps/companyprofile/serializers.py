from rest_framework import serializers

from apps.companyprofile.models import Company
from apps.gallery.serializers import ResponsiveImageSerializer


class CompanySerializer(serializers.ModelSerializer):
    image = ResponsiveImageSerializer()

    class Meta(object):
        model = Company

        fields = (
          'id',
          'name',
          'site',
          'image',
          'long_description',
          'short_description',
        )
