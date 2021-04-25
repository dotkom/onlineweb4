from oauth2_provider.generators import generate_client_secret
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model,
    get_grant_model,
    get_refresh_token_model,
)
from rest_framework import serializers

from apps.sso.models import ApplicationConsent


class SSOClientNonSensitiveSerializer(serializers.ModelSerializer):
    client_type = serializers.ChoiceField(
        choices=["public", "confidential"], allow_blank=True, default="public"
    )
    algorithm = serializers.HiddenField(default="")
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault()) # Read_only means that it can only be set by default

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


class SSOClientConfidentialSerializer(serializers.ModelSerializer):
    redirect_uris = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

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
            "user"
        ]

    def get_redirect_uris(self, obj):
        redirect_uris_string = obj.redirect_uris
        split_on_space = redirect_uris_string.split(" ")
        with_split_on_newline = [
            line for item in split_on_space for line in item.split("\r\n")
        ]
        return with_split_on_newline


class SSOAccessReadOwnSerializer(serializers.ModelSerializer):
    """
    This should only be given to the owner or a superuser.
    Used for getting non-sensitive information to be able to see if an application can currently get data on your behalf.
    """
    class Meta:
        model = get_access_token_model()
        fields = [
            "id",
            "scope",
            "application",
            "created",
            "expired",
            "user"
        ]


class SSORefreshTokenSerializer(serializers.ModelSerializer):
    """
    This should only be given to the owner or a superuser.
    Used for getting information to be able to see if an application can keep querying for access tokens on your behalf.
    """
    class Meta:
        model = get_refresh_token_model()
        fields = [
            "id",
            "created",
            "updated",
            "revoked",
            "user",
            "application"
        ]


class SSOGrantSerializer(serializers.ModelSerializer):
    """
    This should only be given to the owner or a superuser.
    It represents a login attempt, but contains no information regarding whether it was successful or not.
    """
    class Meta:
        model = get_grant_model()
        fields = [
            "id",
            "user",
            "application",
            "created"
        ]


class SSOApplicationConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationConsent
        fields = [
            "id",
            "date_given",
            "approved_scopes",
            "user",
            "client"
        ]
