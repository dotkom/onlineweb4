from rest_framework import fields, serializers
from .models import CommitteeUpdate
from apps.authentication.models import OnlineGroup, GroupMember
from apps.authentication.serializers import OnlineGroupReadOnlySerializer


class CommitteeUpdateCreateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=1000)
    group_id = serializers.IntegerField()


class CommitteeUpdateReadOnlySerializer(serializers.ModelSerializer):
    group = OnlineGroupReadOnlySerializer()
    
    class Meta:
        model = CommitteeUpdate
        fields = (
            "id",
            "content",
            "created_at",
            "updated_at",
            "group",
        )
        read_only=True