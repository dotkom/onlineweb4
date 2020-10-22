from rest_framework import serializers

from .models import MailEntity, MailGroup


class MailGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailGroup
        fields = ("id", "email", "name", "description", "public")


class MailEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MailEntity
        fields = ("id", "email", "name", "description", "public")
