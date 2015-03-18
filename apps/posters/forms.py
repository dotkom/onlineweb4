from django import forms

from apps.posters.models import Poster


class AddPosterForm(forms.ModelForm):
    
    class Meta:
        model = Poster
        fields = ['title', 'company', 'location', 'when', 'category', 'amount', 'description', 
                  'price', 'display_from', 'display_to', 'comments']

class EditPosterForm(forms.ModelForm):
    
    class Meta:
        model = Poster
        fields = ['title', 'company', 'location', 'when', 'category', 'amount', 'description', 
                  'price', 'display_to', 'display_from', 'comments', 'finished']
