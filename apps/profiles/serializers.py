from rest_framework import serializers

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import PositionSerializer, SpecialPositionSerializer
from apps.profiles.models import Privacy


class ProfileSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField()
    positions = PositionSerializer(many=True)
    special_positions = SpecialPositionSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "username", "nickname", "ntnu_username", "year", "email", "online_mail",
            "phone_number", "address", "website", "github", "linkedin", "positions", "special_positions", "rfid",
            "field_of_study", "started_date", "compiled", "infomail", "jobmail", "zip_code", "allergies",
            "mark_rules", "gender", "bio", "saldo", "is_committee", "is_member", "image", "has_expiring_membership",
        )
        read_only_fields = (
            "username", "ntnu_username", "online_mail", "field_of_study", "started_date", "compiled", "saldo",
        )

def _expose_field(obj, user_field, privacy_field):
    privacy = Privacy.objects.get(user=obj)
    expose = getattr(privacy, privacy_field)
    if expose:
        return getattr(obj, user_field)
    return None

class PublicProfileSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    zip_code = serializers.SerializerMethodField()

    positions = PositionSerializer(many=True)
    special_positions = SpecialPositionSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "nickname",
            "first_name",
            "last_name",
            "phone_number",
            "online_mail",
            "address",
            "zip_code",
            "email",
            "website",
            "github",
            "linkedin",
            "ntnu_username",
            "field_of_study",
            "year",
            "bio",
            "positions",
            "special_positions",
            "image",
            "started_date",
        )

    def get_address(self, obj):
        return _expose_field(obj, 'address', 'expose_address')

    def get_nickname(self, obj):
        return _expose_field(obj, 'nickname', 'expose_nickname')

    def get_email(self, obj):
        return _expose_field(obj, 'email', 'expose_email')

    def get_phone_number(self, obj):
        return _expose_field(obj, 'phone_number', 'expose_phone_number')

    def get_zip_code(self, obj):
        return _expose_field(obj, 'zip_code', 'expose_address')


class PrivacySerializer(serializers.ModelSerializer):

    class Meta:
        model = Privacy
        fields = (
            'visible_for_other_users',
            'expose_nickname',
            'expose_email',
            'expose_phone_number',
            'expose_address',
            'visible_as_attending_events',
        )
