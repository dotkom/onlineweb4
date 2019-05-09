from onlineweb4.fields.recaptcha import RecaptchaField
from rest_framework import serializers

from apps.authentication.fields import OnlineUserEmailField
from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.authentication.models import Position, SpecialPosition
from apps.authentication.utils import send_register_verification_email


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
            'first_name', 'last_name', 'password', 'email', 'username', 'recaptcha'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    email = OnlineUserEmailField(required=True)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'rfid', 'password', 'email', 'username', 'infomail', 'jobmail', 'nickname',
            'website', 'github', 'linkedin', 'gender', 'bio', 'ntnu_username', 'password', 'phone',
        )


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
