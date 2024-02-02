import hashlib
import random
import string

from django.contrib.auth.models import Group, Permission
from django.utils.timezone import datetime
from guardian.shortcuts import get_objects_for_user
from rest_framework import serializers

from apps.authentication.models import (
    Email,
    GroupMember,
    GroupRole,
    Membership,
    OnlineGroup,
)
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition
from apps.gallery.models import ResponsiveImage
from apps.gallery.serializers import ResponsiveImageSerializer


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "username")


class UserReadOnlySerializer(serializers.ModelSerializer):
    rfid = serializers.HiddenField(default="")

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "rfid", "username")
        read_only = True


class AnonymizeUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField()

    def validate_password(self, password):
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Serializer missing request")

        user: User = request.user
        if user.has_usable_password() and not user.check_password(password):
            raise serializers.ValidationError("Nåværende passord stemmer ikke")

        return password

    def validate_username(self, username):
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Serializer missing request")

        user: User = request.user
        if user.get_username() != username:
            raise serializers.ValidationError("Dette er ikke riktig bruker")

        return username

    def update(self, instance: User, validated_data: dict):
        salt = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
        username = hashlib.sha256(
            str(instance.username + salt).encode("utf-8")
        ).hexdigest()
        password = hashlib.sha256(str(salt).encode("utf-8")).hexdigest()

        # Related fields
        if instance.member() is not None:
            Membership.objects.get(username=instance.member().username).delete()
        instance.email_user.all().delete()
        instance.positions.all().delete()
        instance.special_positions.all().delete()
        instance.group_memberships.all().delete()

        # Django related fields
        instance.first_name = ""
        instance.last_name = ""
        instance.email = ""
        instance.passord = instance.set_password(password)
        instance.username = username
        instance.groups.clear()
        instance.user_permissions.clear()
        instance.is_staff = False
        instance.is_active = False
        instance.is_superuser = False
        instance.last_login = datetime(2000, 1, 1)
        instance.date_joined = datetime(2000, 1, 1)

        # Online related fields
        instance.field_of_study = 0
        instance.started_date = datetime(2000, 1, 1)
        instance.compiled = False

        # Mail
        instance.infomail = False
        instance.jobmail = False
        instance.online_mail = None

        # Address
        instance.phone_number = None
        instance.address = None
        instance.zip_code = None

        # Other
        instance.allergies = None
        instance.rfid = None
        instance.nickname = None
        instance.website = None
        instance.github = None
        instance.linkedin = None
        instance.gender = "male"
        instance.bio = ""

        # NTNU credentials
        instance.ntnu_username = None

        instance.save()
        return instance

    class Meta:
        model = User
        fields = ("username", "password")


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "rfid",
            "email",
            "username",
            "infomail",
            "jobmail",
            "nickname",
            "website",
            "github",
            "linkedin",
            "gender",
            "bio",
            "ntnu_username",
            "phone_number",
            "id",
        )


class PermissionReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("content_type", "codename")
        read_only = True


class PositionReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ("id", "committee", "position", "period", "period_start", "period_end")
        read_only = True


class PositionCreateAndUpdateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    period_start = serializers.DateField(required=True, allow_null=False)
    period_end = serializers.DateField(required=True, allow_null=False)

    def validate(self, data):
        period_start = data.get("period_start")
        period_end = data.get("period_end")

        if any([period_end, period_start]) and not all([period_end, period_start]):
            raise serializers.ValidationError(
                "For å endre perioden på vervet må du oppgi verdier for start og slutt"
            )

        if period_start > period_end:
            raise serializers.ValidationError(
                "Vervets starttid kan ikke være etter vervets sluttid"
            )
        if period_start == period_end:
            raise serializers.ValidationError(
                "Du kan ikke starte og avslutte et verv på samme dag"
            )

        return data

    class Meta:
        model = Position
        fields = (
            "id",
            "committee",
            "position",
            "period",
            "period_start",
            "period_end",
            "user",
        )


class SpecialPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialPosition
        fields = ("id", "since_year", "position")
        read_only = True


class EmailReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ("id", "email", "primary", "verified")
        extra_kwargs = {"user": {"write_only": True}}
        read_only = True


class GroupReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")
        read_only = True


class GroupRoleReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRole
        fields = ("id", "role_type", "verbose_name")
        read_only = True


class GroupMemberReadOnlySerializer(serializers.ModelSerializer):
    user = UserNameSerializer()

    class Meta:
        model = GroupMember
        fields = ("id", "user", "added", "roles", "is_on_leave", "is_retired")
        read_only = True


class GroupMemberCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        required=True, queryset=User.objects.all()
    )
    group = serializers.PrimaryKeyRelatedField(
        required=True, queryset=OnlineGroup.objects.all()
    )
    roles = serializers.PrimaryKeyRelatedField(
        required=False, queryset=GroupRole.objects.all(), many=True
    )

    class Meta:
        model = GroupMember
        fields = ("id", "user", "group", "added", "roles", "is_on_leave", "is_retired")
        read_only_fields = ("added",)


class GroupMemberUpdateSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        required=False, queryset=GroupRole.objects.all(), many=True
    )

    class Meta:
        model = GroupMember
        fields = ("id", "user", "group", "added", "roles", "is_on_leave", "is_retired")
        read_only_fields = ("added", "user", "group")


class OnlineGroupReadOnlySerializer(serializers.ModelSerializer):
    image = ResponsiveImageSerializer()

    class Meta:
        model = OnlineGroup
        fields = (
            "id",
            "image",
            "name_short",
            "name_long",
            "name_short",
            "description_long",
            "description_short",
            "application_description",
            "email",
            "created",
            "group_type",
            "verbose_type",
            "group",
            "members",
        )
        read_only = True


class OnlineGroupCreateOrUpdateSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Group.objects.all()
    )
    image = serializers.PrimaryKeyRelatedField(
        required=False, queryset=ResponsiveImage.objects.all()
    )
    parent_group = serializers.PrimaryKeyRelatedField(
        required=False, queryset=OnlineGroup.objects.all()
    )

    def validate_group(self, group: Group):
        if OnlineGroup.objects.filter(group__pk=group.id).exists():
            raise serializers.ValidationError(
                "Denne Djangogruppen har allerede en Onlinegruppe"
            )

        return group

    def validate_parent_group(self, parent_group: OnlineGroup):
        user = self.context.get("user")
        permitted_groups = get_objects_for_user(
            user=user, perms="authentication.change_onlinegroup", klass=OnlineGroup
        )
        can_edit_group = permitted_groups.filter(pk=parent_group.id).exists()
        if not can_edit_group:
            raise serializers.ValidationError(
                f"Du har ikke rettigheter til å administrere gruppen '{parent_group}'"
            )

        return parent_group

    class Meta:
        model = OnlineGroup
        fields = (
            "id",
            "group",
            "image",
            "name_short",
            "name_long",
            "description_short",
            "description_long",
            "application_description",
            "email",
            "group_type",
            "parent_group",
            "sub_groups",
        )
        read_only_fields = ("sub_groups",)
