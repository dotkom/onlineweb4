from rest_framework import serializers
from oauth2_provider.models import (
    get_application_model,
    get_access_token_model,
    get_refresh_token_model,
    get_grant_model,
)
from apps.sso.models import ApplicationConsent

# TODO:
# Remove oauth2 from names, find a better naming


class Oauth2ClientNonSensitiveSerializer(serializers.ModelSerializer):
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


class Oauth2ClientReadOwnSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_application_model()  # Allows for swappable application model
        fields = "__all__"


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
