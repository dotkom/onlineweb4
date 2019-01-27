from rest_framework import serializers

from apps.marks.models import Mark, Suspension


class MarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mark
        fields = (
            'title',
            'added_date',
            'last_changed_date',
            'description',
            'category',
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
