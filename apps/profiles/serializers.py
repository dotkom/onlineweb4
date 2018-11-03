from rest_framework import serializers

from apps.authentication.models import OnlineUser as User
from apps.profiles.models import Privacy

class ProfileSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    online_mail = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = (
            "username", "nickname", "first_name", "last_name", "phone_number", "online_mail"
        )

    def get_nickname(self, object):
        expose_nickname = Privacy.objects.get(user=object).expose_nickname
        if expose_nickname:
            return object.nickname
        else:
            return ""

    def get_online_mail(self, object):
        expose_mail = Privacy.objects.get(user=object).expose_email
        if expose_mail:
            return object.online_mail
        else:
            return ""

    def get_phone_number(self, object):
        expose_phone_number = Privacy.objects.get(user=object).expose_phone_number
        if expose_phone_number:
            return object.phone_number
        else:
            return ""
