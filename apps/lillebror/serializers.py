from rest_framework import serializers

from apps.authentication.serializers import PositionReadOnlySerializer, SpecialPositionSerializer
from apps.authentication.models import OnlineUser as User


class ProfileSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField()
    positions = PositionReadOnlySerializer(many=True)
    special_positions = SpecialPositionSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "username", "nickname", "ntnu_username", "year", "email", "online_mail",
            "phone_number", "address", "website", "github", "linkedin", "positions", "special_positions", "rfid",
            "field_of_study", "started_date", "compiled", "infomail", "jobmail", "zip_code", "allergies",
            "mark_rules", "gender", "bio", "saldo", "is_committee", "is_member", "image", "has_expiring_membership",
            "username", "ntnu_username", "online_mail", "field_of_study", "started_date", "compiled", "saldo",
        )
