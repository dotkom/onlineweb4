from oidc_provider.models import Client, ResponseType, UserConsent
from rest_framework import serializers
from hashlib import sha224
from uuid import uuid4
from random import randint
from apps.authentication.serializers import UserNameSerializer


class ResponseTypeReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseType
        read_only = True
        fields = ("id", "value", "description")


class UserConsentReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConsent
        read_only = True
        fields = ("id", "date_given", "expires_at", "client", "scope", "has_expired")


class ClientReadOwnSerializer(serializers.ModelSerializer):
    response_types = ResponseTypeReadOnlySerializer(many=True)

    class Meta:
        model = Client
        ordering = ["-id"]
        fields = (
            "id",
            "name",
            "owner",
            "date_created",
            "website_url",
            "terms_url",
            "contact_email",
            "logo",
            "require_consent",
            "reuse_consent",
            "scope",
            "response_types",
            "client_secret",
            "client_id",
            "client_type",
            "redirect_uris"
        )


class ClientCreateAndUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    require_consent = serializers.HiddenField(default=True)
    reuse_consent = serializers.HiddenField(default=True)

    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "owner",
            "date_created",
            "website_url",
            "terms_url",
            "contact_email",
            "logo",
            "require_consent",
            "reuse_consent",
            "scope",
            "response_types",
        )
        read_only_fields = ("date_created", "reuse_consent", "require_consent", "scope")


class ClientReadOnlySerializer(serializers.ModelSerializer):
    owner = UserNameSerializer()

    class Meta:
        model = Client
        read_only = True
        fields = (
            "id",
            "name",
            "owner",
            "date_created",
            "website_url",
            "terms_url",
            "contact_email",
            "logo",
            "require_consent",
            "reuse_consent",
            "scope",
            "response_types",
            "client_id",
            "client_type",
        )
