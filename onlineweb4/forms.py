from django import forms


class ErrorForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control error-form'}), label='Fortell oss hvordan du kom hit:')

