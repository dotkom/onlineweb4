from django import forms

from apps.careeropportunity.models import CareerOpportunity
from apps.dashboard.widgets import DatetimePickerInput


class AddCareerOpportunityForm(forms.ModelForm):
    title = forms.CharField(
        label="Tittel",
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Tittel for karrieremuligheten"}),
    )
    ingress = forms.CharField(
        label="Ingress",
        required=True,
        max_length=250,
        widget=forms.Textarea(
            attrs={"placeholder": "Kort ingress til karrieremuligheten (Max 250 tegn)"}
        ),
    )
    description = forms.CharField(
        label="Beskrivelse",
        required=True,
        widget=forms.Textarea(
            attrs={"placeholder": "Detaljert beskrivelse av karrieremuligheten"}
        ),
    )
    application_link = forms.URLField(
        label="Søknadslenke",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Søknadslenke"}),
    )
    application_email = forms.EmailField(
        label="Søknadsepost - brukes kun om søknadslenke mangler",
        required=False,
    )
    start = forms.DateTimeField(
        label="Start-tid",
        required=True,
        widget=DatetimePickerInput(),
    )
    end = forms.DateTimeField(
        label="Slutt-tid",
        required=True,
        widget=DatetimePickerInput(),
    )
    deadline = forms.DateTimeField(
        label="Søknadsfrist",
        required=False,
        widget=DatetimePickerInput(),
    )
    deadline_asap = forms.BooleanField(label="Frist er snarest", required=False)
    rolling_admission = forms.BooleanField(label="Løpende opptak", required=False)

    class Meta:
        model = CareerOpportunity
        fields = (
            "company",
            "title",
            "ingress",
            "description",
            "application_link",
            "application_email",
            "start",
            "end",
            "featured",
            "deadline",
            "deadline_asap",
            "employment",
            "location",
        )
