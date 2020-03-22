from rest_framework import serializers

from .models import Mailinglist


class MailinglistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailinglist
        fields = ("id", "email", "name", "description", "public", "members")
