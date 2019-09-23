from rest_framework import serializers

from apps.authentication.serializers import UserNameSerializer
from oidc_provider.models import UserConsent, Client, ResponseType


class UserConsentReadOnlySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserConsent
        read_only = True
        fields = ('date_given', 'expires_at', 'client', 'scope', 'has_expired',)


class ClientCreateAndUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    require_consent = serializers.HiddenField(default=True)
    reuse_consent = serializers.HiddenField(default=True)

    class Meta:
        model = Client
        fields = (
            'name', 'owner', 'date_created', 'website_url', 'terms_url', 'contact_email', 'logo', 'require_consent',
            'reuse_consent', 'scope', 'response_types',
        )
        read_only_fields = ('date_created', 'reuse_consent', 'require_consent',)


class ClientReadOnlySerializer(serializers.ModelSerializer):
    owner = UserNameSerializer()

    class Meta:
        model = Client
        read_only = True
        fields = (
            'name', 'owner', 'date_created', 'website_url', 'terms_url', 'contact_email', 'logo', 'require_consent',
            'reuse_consent', 'scope', 'response_types',
        )


class ResponseTypeReadOnlySerializer(serializers.ModelSerializer):

    class Meta:
        model = ResponseType
        read_only = True
        fields = ('value', 'description',)
