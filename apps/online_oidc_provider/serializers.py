from hashlib import sha224
from random import randint
from uuid import uuid4

from oidc_provider.models import Client, ResponseType, UserConsent
from rest_framework import serializers

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
            "redirect_uris",
        )


class ClientCreateAndUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    require_consent = serializers.HiddenField(default=True)
    reuse_consent = serializers.HiddenField(default=True)
    redirect_uris = serializers.ListField(child=serializers.CharField())

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
            "redirect_uris",
            "client_type",
            "client_id",
            "client_secret",
        )
        read_only_fields = (
            "date_created",
            "reuse_consent",
            "require_consent",
            "scope",
            "client_id",
            "client_secret",
        )

    def create(self, validated_data):
        client_id = str(randint(1, 999999)).zfill(6)
        client_secret = ""
        if validated_data.get("client_type") == "confidential":
            client_secret = sha224(uuid4().hex.encode()).hexdigest()
        response_type = validated_data.pop("response_types")
        data = {
            **validated_data,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        print(data)
        client = Client.objects.create(**data)
        client.response_types.set(response_type)
        client.save()
        return client

    def update(self, instance, validated_data):
        client_secret = instance.client_secret
        print("Received data:", validated_data, flush=True)
        print("Instance", instance)
        print("Self", self)
        if (
            validated_data.get("client_type") == "confidential"
            and not instance.client_secret
        ):
            client_secret = sha224(uuid4().hex.encode()).hexdigest()
        elif validated_data.get("client_type") == "public" and instance.client_secret:
            client_secret = ""
        data = {**validated_data, "client_secret": client_secret}
        for key, value in data.items():
            print("Setting ", key, "to value", value, flush=True)
            setattr(instance, key, value)
        instance.save()
        return instance


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
