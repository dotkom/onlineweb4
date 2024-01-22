# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import Group
from guardian.shortcuts import get_perms_for_model

from apps.dashboard.widgets import DatePickerInput, DatetimePickerInput
from apps.events.models import AttendanceEvent, CompanyEvent, Event, Reservation
from apps.feedback.models import Feedback, FeedbackRelation
from apps.gallery.constants import ImageFormat
from apps.gallery.widgets import SingleImageInput
from apps.payment.models import Payment, PaymentPrice


class CreateEventForm(forms.ModelForm):
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

        widgets = {
            "event_start": DatetimePickerInput(),
            "event_end": DatetimePickerInput(),
            "image": SingleImageInput(
                attrs={"id": "responsive-image-id", "preset": ImageFormat.EVENT}
            ),
        }


class CreateAttendanceEventForm(forms.ModelForm):
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

        widgets = {
            "registration_start": DatetimePickerInput(),
            "registration_end": DatetimePickerInput(),
            "unattend_deadline": DatetimePickerInput(),
        }


class AddCompanyForm(forms.ModelForm):
    class Meta:
        model = CompanyEvent
        fields = ("company",)


class ChangeEventForm(forms.ModelForm):
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

        widgets = {
            "event_start": DatetimePickerInput(),
            "event_end": DatetimePickerInput(),
        }


class ChangeAttendanceEventForm(forms.ModelForm):
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

        widgets = {
            "registration_start": DatetimePickerInput(),
            "registration_end": DatetimePickerInput(),
            "unattend_deadline": DatetimePickerInput(),
        }


class CreateFeedbackRelationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        feedback = Feedback.objects.filter(available=True)
        self.fields["feedback"].queryset = feedback

    class Meta:
        model = FeedbackRelation
        fields = ("feedback", "deadline", "gives_mark")
        widgets = {"deadline": DatePickerInput}


class CreatePaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("stripe_key", "payment_type", "deadline", "delay")

        widgets = {
            "deadline": DatetimePickerInput(),
        }


class CreatePaymentPriceForm(forms.ModelForm):
    class Meta:
        model = PaymentPrice
        fields = ("price", "description")


class ChangeReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        exclude = ["attendance_event"]
