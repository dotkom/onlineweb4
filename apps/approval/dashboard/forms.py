from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.dashboard.widgets import DatetimePickerInput

from ..models import CommitteeApplicationPeriod


class CommitteeApplicationPeriodForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.copy()
        data.pop("committees")
        period = CommitteeApplicationPeriod(**data)

        minimum_duration = timezone.timedelta(days=1)
        if period.start + minimum_duration >= period.deadline:
            raise ValidationError("En opptaksperiode må vare i minst én dag")

        actual_deadline = period.deadline + period.deadline_delta
        overlapping_periods = CommitteeApplicationPeriod.objects.filter_overlapping(
            period.start, actual_deadline
        )

        if self.instance:
            overlapping_periods = overlapping_periods.exclude(pk=self.instance.pk)

        if overlapping_periods.exists():
            raise ValidationError("Opptaksperioder kan ikke overlappe med hverandre")

        return cleaned_data

    class Meta:
        model = CommitteeApplicationPeriod
        fields = ("title", "start", "deadline", "deadline_delta", "committees")

        widgets = {
            "start": DatetimePickerInput(),
            "deadline": DatetimePickerInput(),
        }


class ApplicationPeriodParticipantsUpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        application_period: CommitteeApplicationPeriod = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        self.fields["committees_with_applications"].choices = [
            (participation.pk, participation.onlinegroup.name_short)
            for participation in application_period.committeeapplicationperiodparticipation_set.all()
        ]

    committees_with_applications = forms.MultipleChoiceField(
        label="Komiteer som har opptak, de som ikke har opptak vil allikevel vises i opptaksperioden, men uten at en "
        "kan søke direkte til den komiteen.",
        required=False,
    )
