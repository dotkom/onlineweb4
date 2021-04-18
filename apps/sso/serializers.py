from rest_framework import serializers
from oauth2_provider.models import (
    get_application_model,
    get_access_token_model,
    get_refresh_token_model,
    get_grant_model,
)
from apps.sso.models import ApplicationConsent
from oauth2_provider.generators import generate_client_secret

# TODO:
# Remove oauth2 from names, find a better naming


class Oauth2ClientNonSensitiveSerializer(serializers.ModelSerializer):
    client_type = serializers.ChoiceField(
        choices=["public", "confidential"], allow_blank=True, default="public"
    )
    algorithm = serializers.HiddenField(default="")
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

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


class Oauth2ClientSerializer(serializers.ModelSerializer):
    redirect_uris = serializers.SerializerMethodField()

    class Meta:
        model = get_application_model()  # Allows for swappable application model
        fields = "__all__"

    def get_redirect_uris(self, obj):
        redirect_uris_string = obj.redirect_uris
        split_on_space = redirect_uris_string.split(" ")
        with_split_on_newline = [
            line for item in split_on_space for line in item.split("\r\n")
        ]
        return with_split_on_newline


class Oauth2AccessReadOwnSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_access_token_model()
        fields = "__all__"


class Oauth2RefreshTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_refresh_token_model()
        fields = "__all__"


class Oauth2GrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_grant_model()
        fields = "__all__"


class Oauth2ApplicationConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationConsent
        fields = "__all__"
