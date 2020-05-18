# -*- coding: utf-8 -*-

from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.authentication.constants import FieldOfStudyType

SEMESTER_CHOICES = [("h", _("Høst")), ("v", _("Vår"))]

VALID_FIELD_OF_STUDY_CHOICES = filter(
    lambda choice: choice[0] != FieldOfStudyType.GUEST, FieldOfStudyType.ALL_CHOICES
)


def _year_choices():
    now = timezone.now()
    years = list(range(now.year - 10, now.year + 1))
    return list(zip(years[::-1], years[::-1]))


class FieldOfStudyApplicationForm(forms.Form):
    started_semester = forms.ChoiceField(
        label=_("Hvilket semester startet du? "), choices=SEMESTER_CHOICES
    )
    started_year = forms.ChoiceField(
        label=_("Hvilket år startet du? "), choices=_year_choices()
    )
    field_of_study = forms.ChoiceField(
        label=_("Studieretning "), choices=VALID_FIELD_OF_STUDY_CHOICES
    )
    documentation = forms.ImageField(label=_("Dokumentasjon "), required=False)
