from rest_framework import serializers

from apps.hobbygroups.models import Hobby
from apps.gallery.serializers import ResponsiveImageSerializer


class HobbySerializer(serializers.ModelSerializer):

    image = ResponsiveImageSerializer()

    class Meta:
        model = Hobby
        fields = ('id', 'title', 'description', 'read_more_link', 'image')
