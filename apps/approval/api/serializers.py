from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

from apps.authentication.constants import FieldOfStudyType
from apps.authentication.models import OnlineGroup
from apps.authentication.serializers import UserReadOnlySerializer

from ..models import (
    CommitteeApplication,
    CommitteeApplicationPeriod,
    CommitteeApplicationPeriodParticipation,
    CommitteePriority,
    MembershipApproval,
)


class CommitteeSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField(source="group")

    class Meta:
        model = CommitteePriority
        fields = ("group", "group_name", "priority")

    def get_group_name(self, instance):
        return instance.group.name_long


class CommitteeApplicationPeriodParticipationSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="onlinegroup", queryset=OnlineGroup.objects.all()
    )

    class Meta:
        model = CommitteeApplicationPeriodParticipation
        fields = ("id", "open_for_applications")


class CommitteeApplicationPeriodSerializer(serializers.ModelSerializer):
    # Define annotated fields manually since they can't be inferred from the class
    actual_deadline = serializers.DateTimeField(read_only=True)
    accepting_applications = serializers.BooleanField(read_only=True)
    committees = CommitteeApplicationPeriodParticipationSerializer(
        source="committeeapplicationperiodparticipation_set", many=True, read_only=True
    )

    def validate(self, attrs: dict):
        # Validate on a class instance instead of on the attrs themselves.
        # This lets us use instance properties and default values correctly.
        # Use request data without the 'many'-related properties, as they can't be added directly in the class.
        data = attrs.copy()
        if "committees" in data:
            del data["committees"]
        period = CommitteeApplicationPeriod(**data)

        minimum_duration = timezone.timedelta(days=1)
        if period.start + minimum_duration >= period.deadline:
            raise serializers.ValidationError(
                "En opptaksperiode må vare i minst én dag"
            )

        overlapping_periods = CommitteeApplicationPeriod.objects.filter_overlapping(
            period.start, period.actual_deadline_method()
        )

        if self.instance:
            overlapping_periods = overlapping_periods.exclude(pk=self.instance.pk)

        if overlapping_periods.exists():
            raise serializers.ValidationError(
                "Opptaksperioder kan ikke overlappe med hverandre"
            )

        return attrs

    class Meta:
        model = CommitteeApplicationPeriod
        fields = (
            "id",
            "title",
            "start",
            "deadline",
            "deadline_delta",
            "actual_deadline",
            "committees",
            "accepting_applications",
            "year",
        )


class CommitteeApplicationSerializer(serializers.ModelSerializer):
    committees = CommitteeSerializer(many=True, source="committee_priorities")
    applicant = UserReadOnlySerializer(read_only=True)
    application_period = serializers.PrimaryKeyRelatedField(
        required=True, queryset=CommitteeApplicationPeriod.objects.all()
    )

    class Meta:
        model = CommitteeApplication
        fields = (
            "name",
            "email",
            "applicant",
            "application_text",
            "prioritized",
            "committees",
            "application_period",
        )

    def _is_authenticated(self):
        request = self.context.get("request")
        return request.user.is_authenticated

    def validate_application_period(
        self, application_period: CommitteeApplicationPeriod
    ):
        if not application_period.accepting_applications_method():
            raise ValidationError(
                f"Opptaksperioden {application_period} tar ikke lenger imot søknader. "
                f"Opptaket stengte {application_period.deadline}"
            )
        return application_period

    def validate_committees(self, committees):
        committees.sort(key=lambda c: c.get("priority"))
        for i in range(len(committees)):
            committee = committees[i]
            if i + 1 != committee.get("priority"):
                raise serializers.ValidationError(
                    "Prioriteringer er feilformatert. "
                    "Prioriteringer må være en rekke med tall mellom 1 og 3. "
                    "Alle gruper som sendes på ha forkjsellig prioritering."
                )

        return committees

    def validate(self, attrs: dict):
        email = attrs.get("email")
        name = attrs.get("name")

        if not self._is_authenticated() and not (email and name):
            raise ValidationError(
                "Enten en brukerkonto (søker) eller navn og e-postadresse er påkrevd."
            )

        committees_priorities = attrs.get("committee_priorities")
        application_period = attrs.get("application_period")

        committees = [c.get("group") for c in committees_priorities]
        allowed_committees = application_period.committees.all()

        for committee in committees:
            if committee not in allowed_committees:
                raise serializers.ValidationError(
                    f"En av de valgte komiteene er ikke del av dette opptaket, {allowed_committees}, {committees}"
                )

        return super().validate(attrs)

    def create(self, validated_data):
        committees = validated_data.pop("committee_priorities")
        application = super().create(validated_data)

        for committee in committees:
            CommitteePriority.objects.create(
                committee_application=application, **committee
            )

        return application


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

    field_of_study = ChoiceField(choices=FieldOfStudyType.ALL_CHOICES)

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
