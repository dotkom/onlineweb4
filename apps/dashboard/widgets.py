from django import forms

"""
Override the builtin inputs to use the more appropriate input-type, with better browser/OS support than type=text
"""


class DatePickerInput(forms.DateInput):
    input_type = "date"


class DatetimePickerInput(forms.DateTimeInput):
    input_type = "datetime-local"


class TimePickerInput(forms.TimeField):
    input_type = "time"
