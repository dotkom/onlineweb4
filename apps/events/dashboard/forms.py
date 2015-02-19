
from django import forms

from apps.event.models import Event, AttendanceEvent


class ChangeEventForm(forms.ModelForm):
    model = Event


class ChangeAttendanceEventForm(forms.ModelForm):
    model = AttendanceEvent
