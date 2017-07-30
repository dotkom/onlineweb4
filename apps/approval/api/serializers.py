from rest_framework import serializers

from apps.approval.models import CommitteeApplication, CommitteePriority


class CommitteeSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField(source='group')

    class Meta(object):
        model = CommitteePriority
        fields = ('group', 'group_name', 'priority')

    def get_group_name(self, instance):
        return instance.group.name


class CommitteeApplicationSerializer(serializers.ModelSerializer):
    committees = CommitteeSerializer(many=True, source='committeepriority_set')

    class Meta(object):
        model = CommitteeApplication
        fields = ('name', 'email', 'application_text', 'prioritized', 'committees')

    def create(self, validated_data):
        committees = validated_data.pop('committeepriority_set')
        application = CommitteeApplication.objects.create(**validated_data)

        for committee in committees:
            CommitteePriority.objects.create(committee_application=application, **committee)

        return CommitteeApplication.objects.get(pk=application.pk)
