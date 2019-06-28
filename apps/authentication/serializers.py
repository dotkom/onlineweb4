from django.contrib.auth.models import Group
from onlineweb4.fields.recaptcha import RecaptchaField
from rest_framework import serializers

from apps.authentication.constants import RoleType
from apps.authentication.fields import OnlineUserEmailField
from apps.authentication.models import Email, GroupMember, GroupRole, OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition
from apps.authentication.utils import send_register_verification_email
from apps.gallery.models import ResponsiveImage
from apps.gallery.serializers import ResponsiveImageSerializer


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',)


class UserReadOnlySerializer(serializers.ModelSerializer):
    rfid = serializers.HiddenField(default='')

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'rfid', 'username',)
        read_only = True


class UserCreateSerializer(serializers.ModelSerializer):
    recaptcha = RecaptchaField()
    email = OnlineUserEmailField(required=True)

    def create(self, validated_data):
        """
        The recaptcha field is not part of the model, but will still need to be validated.
        All serializer fields will be put into 'Model#create', and 'recaptcha' is removed for the serializer not
        to try and create it on the model-
        """
        validated_data.pop('recaptcha')

        """ Create user with serializer method """
        created_user = super().create(validated_data)

        """ Set default values and related objects to user """
        created_user.is_active = False
        email = Email.objects.create(
            user=created_user,
            email=validated_data.get('email').lower(),
            primary=True,
        )
        created_user.save()

        send_register_verification_email(
            user=created_user,
            email_obj=email,
            request=self.context.get('request', None)
        )

        return created_user

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'password', 'email', 'username', 'recaptcha', 'id',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'rfid', 'password', 'email', 'username', 'infomail', 'jobmail', 'nickname',
            'website', 'github', 'linkedin', 'gender', 'bio', 'ntnu_username', 'password', 'phone', 'id',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class PositionReadOnlySerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ('id', 'committee', 'position', 'period', 'period_start', 'period_end',)
        read_only = True


class PositionCreateAndUpdateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    period_start = serializers.DateField(required=True, allow_null=False)
    period_end = serializers.DateField(required=True, allow_null=False)

    def validate(self, data):
        period_start = data.get('period_start')
        period_end = data.get('period_end')

        if any([period_end, period_start]) and not all([period_end, period_start]):
            raise serializers.ValidationError('For å endre perioden på vervet må du oppgi verdier for start og slutt')

        if period_start > period_end:
            raise serializers.ValidationError('Vervets starttid kan ikke være etter vervets sluttid')
        if period_start == period_end:
            raise serializers.ValidationError('Du kan ikke starte og avslutte et verv på samme dag')

        return data

    class Meta:
        model = Position
        fields = ('id', 'committee', 'position', 'period', 'period_start', 'period_end', 'user',)


class SpecialPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecialPosition
        fields = ('id', 'since_year', 'position',)
        read_only = True


class EmailReadOnlySerializer(serializers.ModelSerializer):

    class Meta:
        model = Email
        fields = ('id', 'email', 'primary', 'verified',)
        extra_kwargs = {
            'user': {'write_only': True}
        }
        read_only = True


class EmailCreateSerializer(serializers.ModelSerializer):
    verified = serializers.BooleanField(default=False)
    primary = serializers.BooleanField(default=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    email = OnlineUserEmailField(required=True)

    class Meta:
        model = Email
        fields = ('id', 'email', 'primary', 'verified', 'user',)
        read_only_fields = ('primary', 'verified', 'user',)


class EmailUpdateSerializer(serializers.ModelSerializer):
    primary = serializers.BooleanField()

    def validate_primary(self, obj: bool):
        """
        User cannot set an email as non-primary by itself.
        It can only be done by setting another email as primary.
        """
        if not obj:
            raise serializers.ValidationError('Kan bare endre primærepost ved å sette en annen som primær')
        return obj

    def update(self, instance: Email, validated_data):
        request = self.context.get('request', None)
        if not request.user:
            raise serializers.ValidationError('Du må være logget inn for å oppdatere epost')

        """ Set old primary email as inactive if this instance is set as primary """
        if validated_data.get('primary', None):
            primary_email: Email = request.user.get_email()
            if primary_email:
                primary_email.primary = False
                primary_email.save()

        return super().update(instance, validated_data)

    class Meta:
        model = Email
        fields = ('id', 'email', 'primary', 'verified',)
        read_only_fields = ('email', 'verified',)


class GroupReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)
        read_only = True


class GroupRoleReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRole
        fields = ('id', 'role_type', 'added', 'verbose_name')
        read_only = True


class GroupRoleCreateSerializer(serializers.ModelSerializer):
    membership = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=GroupMember.objects.all(),
    )

    def validate(self, data):
        role_type: RoleType = data.get('role_type')
        if role_type in RoleType.SINGLUAR_POSITIONS:
            membership: GroupMember = data.get('membership')
            online_group: OnlineGroup = membership.group
            members = online_group.get_members_with_role(role_type)

            if members.count() != 0:
                raise serializers.ValidationError(f'Det finnes allerede et gruppemedlem med rollen "{role_type}"')

        return data

    class Meta:
        model = GroupRole
        fields = ('membership', 'role_type',)


class GroupMemberReadOnlySerializer(serializers.ModelSerializer):
    user = UserNameSerializer()
    roles = GroupRoleReadOnlySerializer(many=True)

    class Meta:
        model = GroupMember
        fields = ('id', 'user', 'added', 'roles',)
        read_only = True


class GroupMemberCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=User.objects.all(),
    )
    group = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=OnlineGroup.objects.all(),
    )

    class Meta:
        model = GroupMember
        fields = ('user', 'group',)


class OnlineGroupReadOnlySerializer(serializers.ModelSerializer):
    group = GroupReadOnlySerializer()
    members = GroupMemberReadOnlySerializer(many=True)
    image = ResponsiveImageSerializer()

    class Meta:
        model = OnlineGroup
        fields = (
            'image', 'name_short', 'name_long', 'name_short', 'description_long', 'description_short',
            'email', 'created', 'group_type', 'verbose_type', 'group', 'members',
        )
        read_only = True


class OnlineGroupCreateOrUpdateSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Group.objects.all()
    )
    image = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=ResponsiveImage.objects.all(),
    )

    def validate_group(self, group: Group):
        if OnlineGroup.objects.filter(group__pk=group.id).exists():
            raise serializers.ValidationError('Denne Djangogruppen har allerede en Onlinegruppe')

        return group

    class Meta:
        model = OnlineGroup
        fields = (
            'group', 'image', 'name_short', 'name_long', 'description_short', 'description_long', 'email',
            'group_type',
        )
