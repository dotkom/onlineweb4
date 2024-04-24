from django import forms
from turnstile.fields import TurnstileField


class ContactForm(forms.Form):
    mail_choices = (
        ("hovedstyret@online.ntnu.no", "Hovedstyret"),
        ("dotkom@online.ntnu.no", "Drifts- og utviklingskomiteen"),
    )
    contact_receiver = forms.ChoiceField(
        required=True, label="Hvem ønsker du å kontakte?", choices=mail_choices
    )
    contact_checkbox = forms.BooleanField(required=False)
    contact_name = forms.CharField(
        required=False,
        widget=forms.TextInput({"placeholder": "Navn", "required": True}),
    )
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput({"placeholder": "Epostadresse", "required": True}),
    )
    content = forms.CharField(
        required=True, widget=forms.Textarea({"placeholder": "Din melding"})
    )
    captcha = TurnstileField(
        error_messages={
            "error_turnstile": ("Du klarte ikke captchaen! Er du en bot?"),
            "invalid_turnstile": ("Du klarte ikke captchaen! Er du en bot?"),
            "required": ("Vennligst vis at du ikke er en bot."),
        }
    )

    def clean(self):
        name = self.cleaned_data.get("contact_name")
        is_anon = self.cleaned_data.get("contact_checkbox")
        email = self.cleaned_data.get("contact_email")

        if not (name and email) and not is_anon:
            error_msg = "Must be filled"
            self.add_error("contact_name", error_msg)
            self.add_error("contact_email", error_msg)
