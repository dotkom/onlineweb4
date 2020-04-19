from rest_framework import serializers

from .models import MailGroup


class MailGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailGroup
        depth = 2
        fields = ("id", "email", "name", "description", "public", "members")
