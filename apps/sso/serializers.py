from oauth2_provider.generators import generate_client_secret
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model,
    get_grant_model,
    get_refresh_token_model,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.sso.models import ApplicationConsent

# Custom fields


class ListOrStringListField(serializers.Field):
    """
    Accepts either a list, space-separated string or new-line separated string.
    Returns a list for retrieve/list methods.
    """

    def to_representation(self, value):
        return value.split()

    def to_internal_value(self, data):
        if type(data) == list:
            return " ".join(data)
        elif type(data) == str:
            return data.replace("\r\n", " ")
        else:
            raise ValidationError("Incorrect format")


# Serializers


class SSOClientNonSensitiveSerializer(serializers.ModelSerializer):
    """
    This should only be used to serialize non-sensitive, non-critical information regarding a client.
    """

    class Meta:
        model = get_application_model()
        fields = [
            "id",
            "client_id",
            "client_type",
            "authorization_grant_type",
            "name",
            "skip_authorization",
            "created",
            "updated",
            "algorithm",
            "scopes",
            "website_url",
            "terms_url",
            "logo",
            "contact_email",
            "user",
        ]
        read_only_fields = ["algorithm", "scopes", "user"]

    def create(self, validated_data):
        client_secret = ""
        if validated_data.get("client_type") == "confidential":
            client_secret = generate_client_secret()
        data = {
            **validated_data,
            "client_secret": client_secret,
        }
        client = get_application_model().objects.create(**data)
        client.save()
        return client


class SSOClientConfidentialSerializer(serializers.ModelSerializer):
    redirect_uris = ListOrStringListField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    client_type = serializers.ChoiceField(
        choices=["public", "confidential"], allow_blank=True, default="public"
    )

    class Meta:
        model = get_application_model()  # Allows for swappable application model
        fields = [
            "id",
            "redirect_uris",
            "client_id",
            "client_type",
            "authorization_grant_type",
            "client_secret",
            "name",
            "skip_authorization",
            "created",
            "updated",
            "algorithm",
            "scopes",
            "website_url",
            "terms_url",
            "logo",
            "contact_email",
            "user",
        ]

    def create(self, validated_data):
        client_secret = ""
        if validated_data.get("client_type") == "confidential":
            client_secret = generate_client_secret()
        data = {
            **validated_data,
            "client_secret": client_secret,
        }
        client = get_application_model().objects.create(**data)
        client.save()
        return client

    def update(self, instance, validated_data):
        client_secret = instance.client_secret
        had_oidc_enabled = instance.algorithm == "RS256"
        will_enable_oidc = (
            not had_oidc_enabled
            and validated_data.get("scopes")
            and "openid" in validated_data.get("scopes")
        )
        algorithm = "RS256" if had_oidc_enabled or will_enable_oidc else ""

        redirect_uris = validated_data.get("redirect_uris")
        print("Redirect uris: ", redirect_uris)

        if (
            validated_data.get("client_type") == "confidential"
            and not instance.client_secret
        ):
            client_secret = generate_client_secret()
        elif validated_data.get("client_type") == "public" and instance.client_secret:
            client_secret = ""

        data = {
            **validated_data,
            "client_secret": client_secret,
            "algorithm": algorithm,
        }
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class SSOAccessReadOwnSerializer(serializers.ModelSerializer):
    """
    This should only be given to the owner or a superuser.
    Used for getting non-sensitive information to be able to see if an application can currently get data on your behalf.
    """

    class Meta:
        model = get_access_token_model()
        fields = ["id", "scope", "application", "created", "expires", "user"]


class SSORefreshTokenSerializer(serializers.ModelSerializer):
    """
    This should only be given to the owner or a superuser.
    Used for getting information to be able to see if an application can keep querying for access tokens on your behalf.
    """

    class Meta:
        model = get_refresh_token_model()
        fields = ["id", "created", "updated", "revoked", "user", "application"]


class SSOGrantSerializer(serializers.ModelSerializer):
    """
    This should only be given to the owner or a superuser.
    It represents a login attempt, but contains no information regarding whether it was successful or not.
    """

    class Meta:
        model = get_grant_model()
        fields = ["id", "user", "application", "created"]


class SSOApplicationConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationConsent
        fields = ["id", "date_given", "approved_scopes", "user", "client"]
