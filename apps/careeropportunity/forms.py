from apps.careeropportunity.models import CareerOpportunity
from django import forms


class AddCareerOpportunityForm(forms.ModelForm):
    description = forms.CharField(label='Beskrivelse', required=True, widget=forms.Textarea(
        attrs={'placeholder': 'Detaljert beskrivelse av karrieremuligheten'}))
    ingress = forms.CharField(label='Ingress', required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Kort ingress til karrieremuligheten'}))

    class Meta:
        model = CareerOpportunity
        fields = ('company', 'title', 'ingress', 'description', 'start', 'end', 'featured')
