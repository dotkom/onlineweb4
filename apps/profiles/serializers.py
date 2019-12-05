from rest_framework import serializers

from apps.authentication.models import OnlineUser as User
from apps.authentication.serializers import (
    PositionReadOnlySerializer,
    SpecialPositionSerializer,
)
from apps.profiles.models import Privacy


class ProfileSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField()
    positions = PositionReadOnlySerializer(many=True)
    special_positions = SpecialPositionSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "nickname",
            "ntnu_username",
            "year",
            "email",
            "online_mail",
            "phone_number",
            "address",
            "website",
            "github",
            "linkedin",
            "positions",
            "special_positions",
            "rfid",
            "field_of_study",
            "started_date",
            "compiled",
            "infomail",
            "jobmail",
            "zip_code",
            "allergies",
            "mark_rules_accepted",
            "gender",
            "bio",
            "saldo",
            "is_committee",
            "is_member",
            "image",
            "has_expiring_membership",
        )
        read_only_fields = (
            "username",
            "ntnu_username",
            "online_mail",
            "field_of_study",
            "started_date",
            "compiled",
            "saldo",
        )


class ExposableUserField(serializers.Field):
    """
    Serializes a field for a user based on the users Privacy settings.

    Defaults to a defined variable naming:
    For a field 'foo' on OnlineUser, the field 'expose_foo' from Privacy will be used.
    This behavior can be overwritten with the 'privacy_field' kwarg.
    """

    def __init__(self, **kwargs):
        self.field_name = kwargs.pop("field_name", None)
        defualt_privacy_field = "expose_{}".format(self.field_name)
        self.privacy_field = kwargs.pop("privacy_field", defualt_privacy_field)
        super(ExposableUserField, self).__init__(**kwargs)

    def get_attribute(self, obj):
        return obj

    def to_representation(self, obj):
        privacy = Privacy.objects.get(user=obj)
        expose = getattr(privacy, self.privacy_field)
        if expose:
            return getattr(obj, self.field_name)
        return None


class PublicProfileSerializer(serializers.ModelSerializer):
    address = ExposableUserField(field_name="address")
    nickname = ExposableUserField(field_name="nickname")
    email = ExposableUserField(field_name="email")
    phone_number = ExposableUserField(field_name="phone_number")
    zip_code = ExposableUserField(field_name="zip_code", privacy_field="expose_address")

    positions = PositionReadOnlySerializer(many=True)
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


class PrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Privacy
        fields = (
            "visible_for_other_users",
            "expose_nickname",
            "expose_email",
            "expose_phone_number",
            "expose_address",
            "visible_as_attending_events",
        )
