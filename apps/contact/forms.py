from django import forms

class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True, label="Ditt navn:")
    contact_email = forms.EmailField(required=True, label="Din epostadresse:")
    content = forms.CharField(required=True, widget=forms.Textarea, label="Din melding:")
