from django import forms
from django.contrib.auth.models import Group
from django.utils import timezone

from apps.dashboard.widgets import DatePickerInput
from apps.events.models import Event
from apps.posters.models import Poster


class AddForm(forms.ModelForm):
    required_css_class = "required"
    # @ToDo: Look at using event field as datalist
    description = forms.CharField(
        label="Plakattekst",
        required=False,
        widget=forms.Textarea(
            attrs={"placeholder": "Detaljert hva du vil ha av tekst på plakaten"}
        ),
    )
    comments = forms.CharField(
        label="Kommentarer",
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Skriv her om du vil bestille plakat og banner eller bare banner. Fyll også inn eventuell informasjon, kommentarer, lenker til bilder, osv..."
            }
        ),
    )
    price = forms.DecimalField(
        label="Pris",
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "Pris på event"}),
    )
    amount = forms.IntegerField(
        label="Antall",
        required=False,
        widget=forms.NumberInput(
            attrs={"placeholder": "Hvor mange vil du ha?", "value": "10"}
        ),
    )
    ordered_committee = forms.ModelChoiceField(
        queryset=Group.objects.all(), empty_label=None
    )

    class Meta:
        model = Poster
        fields = [
            "ordered_committee",
            "amount",
            "description",
            "price",
            "comments",
            "display_from",
        ]

        widgets = {"display_from": DatePickerInput()}


class AddPosterForm(AddForm):
    bong = forms.IntegerField(
        label="Bonger",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Antall bonger du vil ha. La feltet stå tomt hvis du ikke ønsker noen."
            }
        ),
    )
    event = forms.ModelChoiceField(
        label="Event",
        queryset=Event.objects.order_by("-id").exclude(event_start__lte=timezone.now()),
    )

    class Meta:
        model = Poster
        fields = [
            "ordered_committee",
            "event",
            "amount",
            "bong",
            "description",
            "price",
            "display_from",
            "comments",
        ]

        widgets = {"display_from": DatePickerInput()}


class AddBongForm(AddForm):
    pass


class AddOtherForm(AddForm):
    title = forms.CharField(
        label="Tittel",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Tittelen til det du bestiller, vanligvis arrangementnavn"
            }
        ),
    )

    class Meta:
        model = Poster
        fields = [
            "ordered_committee",
            "title",
            "amount",
            "price",
            "description",
            "display_from",
            "comments",
        ]

        widgets = {"display_from": DatePickerInput()}


class EditPosterForm(AddPosterForm):
    class Meta:
        model = Poster
        fields = [
            "event",
            "amount",
            "bong",
            "description",
            "price",
            "display_from",
            "comments",
        ]

        widgets = {"display_from": DatePickerInput()}


class EditOtherForm(AddOtherForm):
    class Meta:
        model = Poster
        fields = ["title", "amount", "price", "description", "display_from", "comments"]
        widgets = {"display_from": DatePickerInput()}
