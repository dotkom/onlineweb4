from rest_framework import serializers

from apps.gallery.serializers import ResponsiveImageSerializer
from apps.hobbygroups.models import Hobby


class HobbySerializer(serializers.ModelSerializer):

    image = ResponsiveImageSerializer()

    class Meta:
        model = Hobby
        fields = ('id', 'title', 'description', 'read_more_link', 'image')
