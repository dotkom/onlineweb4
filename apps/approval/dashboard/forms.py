from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.dashboard.widgets import DatetimePickerInput, multiple_widget_generator

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

        if overlapping_periods.exists():
            raise ValidationError("Opptaksperioder kan ikke overlappe med hverandre")

        return cleaned_data

    class Meta:
        model = CommitteeApplicationPeriod
        fields = ("title", "start", "deadline", "deadline_delta", "committees")

        dtp_fields = (("start", {}), ("deadline", {}))
        widgetlist = [(DatetimePickerInput, dtp_fields)]

        widgets = multiple_widget_generator(widgetlist)


class ApplicationPeriodParticipantsUpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        application_period: CommitteeApplicationPeriod = kwargs.pop("instance")
        super().__init__(*args, **kwargs)
        self.fields["committees_with_applications"].choices = [
            (committee.pk, committee.name_short)
            for committee in application_period.committees.all()
        ]

    committees_with_applications = forms.MultipleChoiceField(
        label="Komiteer som har opptak, de som ikke har opptak vil allikevel vises i opptaksperioden, men uten at en "
        "kan søke direkte til den komiteen.",
        required=False,
    )
