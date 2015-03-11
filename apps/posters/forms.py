from django import forms

from apps.posters.models import Poster


class AddPosterForm(forms.ModelForm):
    
    class Meta:
        model = Poster
        fields = ['title', 'company', 'location', 'when', 'category', 'amount', 'description', 
                  'price', 'display_to', 'display_from', 'comments']

class ChangePosterForm(forms.ModelForm):
    
    class Meta:
        model = Poster
        fields = ['title', 'company', 'location', 'when', 'category', 'amount', 'description', 
                  'price', 'display_to', 'display_from', 'comments', 'finished']
