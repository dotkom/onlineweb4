from rest_framework import serializers

from apps.authentication.serializers import UserNameSerializer
from apps.marks.models import Mark, MarkUser, Suspension


class MarkSerializer(serializers.ModelSerializer):
    given_by = UserNameSerializer()
    last_changed_by = UserNameSerializer()

    class Meta:
        model = Mark
        fields = (
            'title',
            'added_date',
            'last_changed_date',
            'description',
            'category',
            'given_by',
            'last_changed_by',
        )


class MarkUserSerializer(serializers.ModelSerializer):
    mark = MarkSerializer()

    class Meta:
        model = MarkUser
        fields = (
            'expiration_date',
            'mark'
        )


class SuspensionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Suspension
        fields = (
            'title',
            'description',
            'active',
            'added_date',
            'expiration_date',
            'payment_id',
        )
