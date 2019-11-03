from rest_framework import serializers

from apps.gsuite.models import GsuiteAlias, GsuiteGroup


class GsuiteGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GsuiteGroup
        fields = ("email", "name", "description")
        read_only = True


class GsuiteGroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GsuiteGroup
        fields = ("name", "description")
        read_only = True


class GsuiteAliasCreateOrUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GsuiteAlias
        fields = ("email",)
        read_only = True
