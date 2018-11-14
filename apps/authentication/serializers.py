from rest_framework import serializers

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition


class UserSerializer(serializers.ModelSerializer):
    rfid = serializers.HiddenField(default='')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'rfid',)


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ("period", "committee", "position")


class SpecialPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialPosition
        fields = ("since_year", "position")
