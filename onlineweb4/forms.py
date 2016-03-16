from django import forms


class ErrorForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, label='Fortell oss hvordan du kom hit:')

#, label='Fortell oss hvordan du kom hit'