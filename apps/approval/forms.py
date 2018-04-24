# -*- coding: utf-8 -*-

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.authentication.models import FIELD_OF_STUDY_CHOICES

SEMESTER_CHOICES = [
    ("h", _("Høst")),
    ("v", _("Vår")),
]


def _year_choices():
    now = timezone.now()
    years = list(range(now.year - 10, now.year + 1))
    return list(zip(years[::-1], years[::-1]))


class FieldOfStudyApplicationForm(forms.Form):
    started_semester = forms.ChoiceField(
        label=_("Hvilket semester startet du? "), choices=SEMESTER_CHOICES)
    started_year = forms.ChoiceField(
        label=_("Hvilket år startet du? "), choices=_year_choices())
    field_of_study = forms.ChoiceField(
        label=_("Studieretning "), choices=FIELD_OF_STUDY_CHOICES)
    documentation = forms.ImageField(
        label=_("Dokumentasjon "), required=False)
