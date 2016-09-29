from rest_framework import serializers

from apps.authentication.models import OnlineUser as User


class UserSerializer(serializers.ModelSerializer):
    rfid = serializers.HiddenField(default='')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'rfid',)
