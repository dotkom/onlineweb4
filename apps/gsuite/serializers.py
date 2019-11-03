from rest_framework import serializers

from apps.gsuite.models import GroupSync, GsuiteGroup


class GroupSyncReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSync
        fields = ("id", "online_group", "gsuite_group", "group_roles")
        read_only = True


class GsuiteGroupReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = GsuiteGroup
        fields = ("id", "email", "email_name", "main_group")
        read_only = True
