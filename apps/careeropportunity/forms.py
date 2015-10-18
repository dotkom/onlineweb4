from django import forms

from apps.careeropportunity.models import CareerOpportunity


class AddCareerOpportunityForm(forms.ModelForm):
    description = forms.CharField(label=u'Beskrivelse', required=True, widget=forms.Textarea(
        attrs={'placeholder': u'Detaljert beskrivelse av karrieremuligheten'}))
    ingress = forms.CharField(label=u'Ingress', required=True, widget=forms.TextInput(
        attrs={'placeholder': u'Kort ingress til karrieremuligheten'}))

    class Meta:
        model = CareerOpportunity
        fields = ('company', 'title', 'ingress', 'description', 'start', 'end', 'featured')
