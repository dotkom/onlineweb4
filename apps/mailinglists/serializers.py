from rest_framework import serializers

from .models import MailGroup


class MailGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailGroup
        fields = ("id", "email", "name", "description", "public", "members")
