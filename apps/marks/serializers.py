from rest_framework import serializers

from apps.authentication.serializers import UserNameSerializer
from apps.marks.models import Mark, MarkRuleSet, RuleAcceptance, Suspension


class MarkSerializer(serializers.ModelSerializer):
    given_by = UserNameSerializer()
    last_changed_by = UserNameSerializer()
    category_display = serializers.SerializerMethodField()

    def get_category_display(self, mark: Mark):
        return mark.get_category_display()

    class Meta:
        model = Mark
        fields = (
            "title",
            "added_date",
            "last_changed_date",
            "description",
            "category",
            "category_display",
            "given_by",
            "last_changed_by",
        )


class SuspensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suspension
        fields = (
            "title",
            "description",
            "added_date",
            "expiration_date",
            "payment_id",
        )


class MarkRuleSetReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkRuleSet
        fields = ("created_date", "valid_from_date", "content", "version")
        read_only = True


class RuleAcceptanceReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleAcceptance
        fields = ("rule_set", "accepted_date")
        read_only = True


class RuleAcceptanceSerializer(serializers.ModelSerializer):
    rule_set = MarkRuleSetReadOnlySerializer()

    class Meta:
        model = RuleAcceptance
        fields = ("rule_set", "accepted_date")


class RuleAcceptanceCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    rule_set = serializers.PrimaryKeyRelatedField(queryset=MarkRuleSet.objects.all())

    class Meta:
        model = RuleAcceptance
        fields = ("rule_set", "accepted_date", "user")
        read_only_fields = ("accepted_date",)
