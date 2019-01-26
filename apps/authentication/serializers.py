from rest_framework import serializers

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition, Email


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',)


class UserSerializer(serializers.ModelSerializer):
    rfid = serializers.HiddenField(default='')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'rfid', 'password', 'email', 'username',)
        extra_kwargs = {
            'email': {'write_only': True},
            'password': {'write_only': True},
            'username': {'write_only': True},
        }


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ("period", "committee", "position")


class SpecialPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialPosition
        fields = ("since_year", "position")

class EmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Email
        fields = ('email', 'primary', 'verified',)
