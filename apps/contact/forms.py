from captcha.fields import ReCaptchaField
from django import forms


class ContactForm(forms.Form):
    komiteer = ((1, "Hovedstyret"), (2, "Drifts- og utviklingskomiteen"))
    contact_name = forms.CharField(required=True, widget=forms.TextInput({"placeholder": "Navn"}))
    contact_email = forms.EmailField(required=True, widget=forms.TextInput({"placeholder": "Epostadresse"}))
    contact_receiver = forms.ChoiceField(required=True, label="Hvem ønsker du å kontakte?", choices=komiteer)
    content = forms.CharField(required=True, widget=forms.Textarea({"placeholder": "Din melding"}))
    captcha = ReCaptchaField(error_messages={'required': ('Du klarte ikke captchaen! Er du en bot?'),
                                             'invalid': ('Du klarte ikke captchaen! Er du en bot?')})
