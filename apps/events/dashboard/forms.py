# -*- coding: utf-8 -*-

from django import forms

from datetimewidget.widgets import DateTimeWidget
from filebrowser.widgets import FileInput

from apps.events.models import Event, AttendanceEvent, RuleBundle, Reservation


def _get_datetime_widget(field_name):
    return DateTimeWidget(
                          attrs = {'id': field_name + "_datepicker"}, 
                          usel10n = True, 
                          bootstrap_version=3,
                          options = {
                              'format': 'dd/mm/yyyy hh:ii',
                          }
                      )


class ChangeEventForm(forms.ModelForm):
    
    class Meta:
        model = Event
        widgets = {
            'event_start': _get_datetime_widget('event_start'),
            'event_end': _get_datetime_widget('event_end'),
        }
        fields = ['title', 'event_type', 'event_start', 'event_end', 'location', 'ingress_short', 'ingress', 'description', 'image']


class ChangeAttendanceEventForm(forms.ModelForm):
    class Meta:
        model = AttendanceEvent
        widgets = {
            'registration_start': _get_datetime_widget('registration_end'),
            'unattend_deadline': _get_datetime_widget('unattend_deadline'),
            'registration_end': _get_datetime_widget('registration_end'),
        }
        fields = ['max_capacity', 'waitlist', 'guest_attendance', 'automatically_set_marks', 'registration_start', 'unattend_deadline', 'registration_end', 'rule_bundles']


class ChangeReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        exclude = ['attendance_event',]
