from captcha.fields import ReCaptchaField
from django import forms


class ContactForm(forms.Form):
    mail_choices = (("hovedstyret@online.ntnu.no", "Hovedstyret"),
                    ("dotkom@online.ntnu.no", "Drifts- og utviklingskomiteen")
                    )
    contact_name = forms.CharField(widget=forms.TextInput({"placeholder": "Navn"}))
    contact_email = forms.EmailField(widget=forms.TextInput({"placeholder": "Epostadresse"}))
    contact_receiver = forms.ChoiceField(required=True, label="Hvem ønsker du å kontakte?", choices=mail_choices)
    content = forms.CharField(required=True, widget=forms.Textarea({"placeholder": "Din melding"}))
    captcha = ReCaptchaField(error_messages={'required': ('Du klarte ikke captchaen! Er du en bot?'),
                                             'invalid': ('Du klarte ikke captchaen! Er du en bot?')})
