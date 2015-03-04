
from django import forms

from apps.events.models import Event, AttendanceEvent


class ChangeEventForm(forms.ModelForm):
    
    class Meta:
        model = Event
        fields = ['title', 'event_start', 'event_end', 'location', 'ingress_short', 'ingress', 'description']


class ChangeAttendanceEventForm(forms.ModelForm):
    class Meta:
        model = AttendanceEvent
