from rest_framework import serializers


class SlackSerializer(serializers.Serializer):
    email = serializers.EmailField()
