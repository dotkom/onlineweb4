from rest_framework import serializers

from apps.authentication.constants import FieldOfStudyType

from ..models import MembershipApproval


class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        if data == "" and self.allow_blank:
            return ""

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail("invalid_choice", input=data)


class MembershipApprovalSerializer(serializers.ModelSerializer):
    field_of_study = ChoiceField(choices=FieldOfStudyType.choices)

    class Meta:
        model = MembershipApproval
        fields = (
            "id",
            "field_of_study",
            "created",
            "processed",
            "processed_date",
            "approved",
            "message",
            "new_expiry_date",
            "started_date",
        )
