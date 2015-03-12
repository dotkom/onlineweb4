
from django import forms

from datetimewidget.widgets import DateTimeWidget
from filebrowser.widgets import FileInput

from apps.events.models import Event, AttendanceEvent


class ChangeEventForm(forms.ModelForm):

    class Meta:
        model = Event
        widgets = {
            'event_start': DateTimeWidget(
                attrs = {'id': "event_start_datepicker"}, 
                usel10n = True, 
                bootstrap_version=3,
                options = {
                    'format': 'dd/mm/yyyy hh',
                }
            ),
            'event_end': DateTimeWidget(
                attrs = {'id': "event_end_datepicker"}, 
                usel10n = True, 
                bootstrap_version=3,
                options = {
                    'format': 'dd/mm/yyyy hh'
                }
            ),
        }
        fields = ['title', 'event_type', 'event_start', 'event_end', 'location', 'ingress_short', 'ingress', 'description', 'image']


class ChangeAttendanceEventForm(forms.ModelForm):
    class Meta:
        model = AttendanceEvent
        fields = (
                'event', 'max_capacity', 'waitlist', 'guest_attendance',
                'registration_start', 'registration_end', 'unattend_deadline',
                'automatically_set_marks', 'marks_has_been_set', 'rule_bundles',
                )
