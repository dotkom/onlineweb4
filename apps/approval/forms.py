# -*- coding: utf-8 -*-

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.authentication.models import FIELD_OF_STUDY_CHOICES


SEMESTER_CHOICES = [
    ("h", _(u"Høst")),
    ("v", _(u"Vår")),
]


def _year_choices():
    now = timezone.now()
    years = range(now.year-10, now.year+1)
    return zip(years[::-1], years[::-1])


class FieldOfStudyApplicationForm(forms.Form):
    started_semester = forms.ChoiceField(label=_(u"Hvilket semester startet du? "), choices=SEMESTER_CHOICES)
    started_year = forms.ChoiceField(label=_(u"Hvilket år startet du? "), choices=_year_choices())
    field_of_study = forms.ChoiceField(label=_(u"Studieretning "), choices=FIELD_OF_STUDY_CHOICES)
