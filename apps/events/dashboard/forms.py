# -*- coding: utf-8 -*-

from django import forms

from apps.dashboard.forms import HTML5RequiredMixin
from apps.dashboard.widgets import DatetimePickerInput, multiple_widget_generator
from apps.events.models import AttendanceEvent, CompanyEvent, Event, Reservation
from apps.gallery.widgets import SingleImageInput


class CreateEventForm(forms.ModelForm, HTML5RequiredMixin):
    class Meta(object):
        model = Event
        fields = (
            'title', 'event_start', 'event_end', 'location', 'ingress_short', 'ingress', 'description', 'event_type',
            'image'
        )

        img_fields = [('image', {'id': 'responsive-image-id'})]
        dtp_fields = [('event_start', {"placeholder": "Arrangementsstart"}),
                      ('event_end', {"placeholder": "Arrangementsslutt"})]
        widgetlist = [
            (DatetimePickerInput, dtp_fields),
            (SingleImageInput, img_fields)
        ]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)


class CreateAttendanceEventForm(forms.ModelForm, HTML5RequiredMixin):
    class Meta(object):
        model = AttendanceEvent
        fields = (
            'max_capacity', 'registration_start', 'registration_end',
            'unattend_deadline', 'automatically_set_marks', 'waitlist', 'guest_attendance', 'marks_has_been_set',
            'rule_bundles', 'extras'
        )

        dtp_fields = [('registration_start', {"placeholder": ""}), ('registration_end', {"placeholder": ""}),
                      ('unattend_deadline', {"placeholder": ""})]
        widgetlist = [
            (DatetimePickerInput, dtp_fields),
        ]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)


class AddCompanyForm(forms.ModelForm):
    class Meta(object):
        model = CompanyEvent
        fields = ('company',)


class ChangeEventForm(forms.ModelForm, HTML5RequiredMixin):

    class Meta:
        model = Event
        fields = (
            'title', 'event_type', 'event_start', 'event_end', 'location', 'ingress_short', 'ingress', 'description',
            'image'
        )

        dtp_fields = [('event_start', {}), ('event_end', {})]

        widgetlist = [
            (DatetimePickerInput, dtp_fields)
        ]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)


class ChangeAttendanceEventForm(forms.ModelForm, HTML5RequiredMixin):
    class Meta:
        model = AttendanceEvent
        fields = (
            'event', 'max_capacity', 'waitlist', 'guest_attendance',
            'registration_start', 'registration_end', 'unattend_deadline',
            'automatically_set_marks', 'marks_has_been_set', 'rule_bundles',
        )

        dtp_fields = [('registration_start', {}), ('registration_end', {}), ('unattend_deadline', {})]

        widgetlist = [
            (DatetimePickerInput, dtp_fields)
        ]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)


class ChangeReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        exclude = ['attendance_event', ]
