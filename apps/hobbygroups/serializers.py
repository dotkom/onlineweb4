from rest_framework import serializers

from apps.hobbygroups.models import Hobby


class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = ('id', 'title', 'description', 'read_more_link')
