# -*- coding: utf-8 -*-
from turnstile.fields import TurnstileField
from django import forms
from django.conf import settings
from django.utils.translation import gettext as _

from apps.authentication.models import OnlineUser as User
from apps.marks.models import MarkRuleSet


class CaptchaForm(forms.Form):
    phone_number = forms.CharField(
        label=_("Telefonnummer er påkrevd for å være påmeldt et arrangement."),
        error_messages={"required": _("Telefonnummer er påkrevd!")},
    )
    note = forms.CharField(
        label=_(
            "Som gjest ønsker vi at du oppgir din tilhørighet til Online og annen tilleggsinformasjon som f.eks. "
            "hvem du ønsker å sitte med."
        ),
        error_messages={"required": _("Du må fylle inn et notat!")},
        max_length=100,
    )
    mark_rules = forms.BooleanField(
        label=_(
            'Jeg godtar <a href="/profile/#marks" target="_blank">prikkreglene</a>'
        ),
        error_messages={"required": _("Du må godta prikkereglene!")},
    )
    captcha = TurnstileField(
        error_messages={
            "error_turnstile": ("Du klarte ikke captchaen! Er du en bot?"),
            "invalid_turnstile": ("Du klarte ikke captchaen! Er du en bot?"),
            "required": ("Vennligst vis at du er human."),
        }
    )

    def __init__(self, *args, **kwargs):
        self.user: User = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Removing mark rules field if user has already accepted the rules
        if self.user and self.user.is_authenticated:
            if self.user.mark_rules_accepted:
                del self.fields["mark_rules"]

            if self.user.phone_number:
                del self.fields["phone_number"]

            if self.user.is_member:
                del self.fields["note"]

            if not settings.OW4_SETTINGS.get("events", {}).get(
                "ENABLE_RECAPTCHA", True
            ):
                del self.fields["captcha"]

    def clean(self):
        super().clean()
        cleaned_data = self.cleaned_data

        if "mark_rules" in self.fields:
            if "mark_rules" in cleaned_data:
                mark_rules = cleaned_data["mark_rules"]

                if mark_rules:
                    MarkRuleSet.accept_mark_rules(self.user)

        if "phone_number" in self.fields:
            if "phone_number" in cleaned_data:
                phone_number = cleaned_data["phone_number"]

                if phone_number:
                    self.user.phone_number = phone_number
                    self.user.save()

        return cleaned_data
