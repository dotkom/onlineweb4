# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import Group
from guardian.shortcuts import get_perms_for_model

from apps.dashboard.forms import HTML5RequiredMixin
from apps.dashboard.widgets import (
    DatePickerInput,
    DatetimePickerInput,
    multiple_widget_generator,
)
from apps.events.models import AttendanceEvent, CompanyEvent, Event, Reservation
from apps.feedback.models import Feedback, FeedbackRelation
from apps.gallery.widgets import SingleImageInput
from apps.payment.models import Payment, PaymentPrice


class CreateEventForm(forms.ModelForm, HTML5RequiredMixin):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not user.is_superuser:
            # Only allow groups with permission to change events be put as organizer.
            # Filter selectable groups by the group memberships of the current user.
            event_perms = get_perms_for_model(Event)
            event_organizer_groups = Group.objects.filter(
                permissions__in=event_perms
            ).distinct()
            self.fields["organizer"].queryset = event_organizer_groups.filter(user=user)

    class Meta:
        model = Event
        fields = (
            "title",
            "event_start",
            "event_end",
            "location",
            "ingress_short",
            "ingress",
            "description",
            "event_type",
            "image",
            "organizer",
            "visible",
        )

        img_fields = [("image", {"id": "responsive-image-id"})]
        dtp_fields = [
            ("event_start", {"placeholder": "Arrangementsstart"}),
            ("event_end", {"placeholder": "Arrangementsslutt"}),
        ]
        widgetlist = [(DatetimePickerInput, dtp_fields), (SingleImageInput, img_fields)]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)


class CreateAttendanceEventForm(forms.ModelForm, HTML5RequiredMixin):
    class Meta:
        model = AttendanceEvent
        fields = (
            "max_capacity",
            "registration_start",
            "registration_end",
            "unattend_deadline",
            "automatically_set_marks",
            "waitlist",
            "guest_attendance",
            "rule_bundles",
            "extras",
        )

        dtp_fields = [
            ("registration_start", {"placeholder": ""}),
            ("registration_end", {"placeholder": ""}),
            ("unattend_deadline", {"placeholder": ""}),
        ]
        widgetlist = [(DatetimePickerInput, dtp_fields)]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)


class AddCompanyForm(forms.ModelForm):
    class Meta:
        model = CompanyEvent
        fields = ("company",)


class ChangeEventForm(forms.ModelForm, HTML5RequiredMixin):
    class Meta:
        model = Event
        fields = (
            "title",
            "event_type",
            "event_start",
            "event_end",
            "location",
            "ingress_short",
            "ingress",
            "description",
            "image",
            "visible",
        )

        dtp_fields = [("event_start", {}), ("event_end", {})]

        widgetlist = [(DatetimePickerInput, dtp_fields)]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)


class ChangeAttendanceEventForm(forms.ModelForm, HTML5RequiredMixin):
    class Meta:
        model = AttendanceEvent
        fields = (
            "event",
            "max_capacity",
            "waitlist",
            "guest_attendance",
            "registration_start",
            "registration_end",
            "unattend_deadline",
            "automatically_set_marks",
            "rule_bundles",
        )

        dtp_fields = [
            ("registration_start", {}),
            ("registration_end", {}),
            ("unattend_deadline", {}),
        ]

        widgetlist = [(DatetimePickerInput, dtp_fields)]

        # Multiple widget generator merges results from regular widget_generator into a single widget dict
        widgets = multiple_widget_generator(widgetlist)


class CreateFeedbackRelationForm(forms.ModelForm, HTML5RequiredMixin):
    def __init__(self, *args, **kwargs):
        super(CreateFeedbackRelationForm, self).__init__(*args, **kwargs)
        feedback = Feedback.objects.filter(available=True)
        self.fields["feedback"].queryset = feedback

    class Meta:
        model = FeedbackRelation
        fields = ("feedback", "deadline", "gives_mark")

        dp_fields = [("deadline", {})]
        widgetlist = [(DatePickerInput, dp_fields)]
        widgets = multiple_widget_generator(widgetlist)


class CreatePaymentForm(forms.ModelForm, HTML5RequiredMixin):
    class Meta:
        model = Payment
        fields = ("stripe_key", "payment_type", "deadline", "delay")

        dtp_fields = [("deadline", {"placeholder": "Betalingsfrist"})]
        widgetlist = [(DatetimePickerInput, dtp_fields)]
        widgets = multiple_widget_generator(widgetlist)


class CreatePaymentPriceForm(forms.ModelForm, HTML5RequiredMixin):
    class Meta:
        model = PaymentPrice
        fields = ("price", "description")


class ChangeReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        exclude = ["attendance_event"]
