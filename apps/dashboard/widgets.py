# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/18/15

from django.forms.utils import force_text, format_html
from django.forms.widgets import TextInput


DATEPICKER_WIDGET_STRING = """
<div class="input-group dp">\r\n
<span class="input-group-btn datepickerbutton">\r\n
<a href="#" class="btn btn-primary">\r\n
<i class="fa fa-calendar fa-lg"></i></a></span>\r\n
<input class="form-control" id="{id}" name="{name}" type="text" placeholder="{placeholder}" value="{value}" />\r\n
</div>\r\n
"""
DATETIMEPICKER_WIDGET_STRING = """
<div class="input-group dtp">\r\n
<span class="input-group-btn datepickerbutton">\r\n
<a href="#" class="btn btn-primary">\r\n
<i class="fa fa-calendar fa-lg"></i></a></span>\r\n
<input class="form-control" id="{id}" name="{name}" type="text" placeholder="{placeholder}" value="{value}" />\r\n
</div>\r\n
"""

TIMEPICKER_WIDGET_STRING = """
<div class="input-group tp">\r\n
<span class="input-group-btn datepickerbutton">\r\n
<a href="#" class="btn btn-primary">\r\n
<i class="fa fa-calendar fa-lg"></i></a></span>\r\n
<input class="form-control" id="{id}" name="{name}" type="text" placeholder="{placeholder}" value="{value}" />\r\n
</div>\r\n
"""


def widget_generator(klass, fields):
    """
    Takes in a class and a list of tuples consisting of field_name and an attribute dictionary
    :param klass: Class of the input widget
    :param fields: List of tuples mapping field names to attribute dictionaries
    :return: A dict of input widget instances
    """

    widgets = {}

    for field_name, attrs in fields:
        widgets[field_name] = klass(attrs=attrs)

    return widgets


def multiple_widget_generator(klass_field_tuples):
    """
    The multiple widget generator takes in a list of tuples consisting of a field widget class and
    a list of field and attribute tuples for each field.

    Example usage:

    dtp_fields = [
        ('published', {'class': 'highlighted'}),
        ('updated', {})
    ]
    responsive_img_fields = [
        ('article_image', {'id': 'article-image'})
    ]

    widgetlist = [(DatetimePickerInput, dtp_fields), (SingleImageInput, responsive_img_fields)]
    widgets = multiple_widget_generator(widgetlist)

    :param klass_field_tuples:
    :return: A final dictionary containing all field name to field widget mappings for use in ModelForms
    """

    widgets = {}

    for klass, fields in klass_field_tuples:
        for field, widget in widget_generator(klass, fields).items():
            widgets[field] = widget

    return widgets


class DatePickerInput(TextInput):
    """
    This form widget metaclass mixin activates Bootstrap Datetimepicker
    """

    def __init__(self, attrs=None):
        super(DatePickerInput, self).__init__(attrs)
        self.input_type = 'text'

    def render(self, name, value, attrs=None):
        """
        Renders this widget
        :param name: Name attribute of the input type
        :param value: Value, if any
        :param attrs: Dictionary of additional attributes and their values
        :return: HTML
        """

        if value is None:
            value = ''

        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            final_attrs['value'] = format_html('value="{}"', force_text(self._format_value(value)))
        else:
            final_attrs['value'] = ''

        # Kept for backwards compatibility with existing forms.
        final_attrs['placeholder'] = 'Den skal vises fra ...'
        if attrs.get('placeholder', False):
            # Update the placeholder text if supplied.
            final_attrs['placeholder'] = force_text(attrs.get('placeholder'))

        return format_html(
            DATETIMEPICKER_WIDGET_STRING,
            id=force_text(final_attrs['id']),
            name=force_text(final_attrs['name']),
            placeholder=force_text(final_attrs['placeholder']),
            value=final_attrs['value']
        )


class DatetimePickerInput(TextInput):
    """
    This form widget metaclass mixin activates Bootstrap Datetimepicker
    """

    def __init__(self, attrs=None):
        super(DatetimePickerInput, self).__init__(attrs)
        self.input_type = 'text'

    def render(self, name, value, attrs=None):
        """
        Renders this widget
        :param name: Name attribute of the input type
        :param value: Value, if any
        :param attrs: Dictionary of additional attributes and their values
        :return: HTML
        """

        if value is None:
            value = ''

        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            final_attrs['value'] = force_text(self._format_value(value))
        else:
            final_attrs['value'] = ''

        # Kept for backwards compatibility with existing forms.
        final_attrs['placeholder'] = 'Den skal vises fra ...'
        if attrs.get('placeholder', False):
            # Update the placeholder text if supplied.
            final_attrs['placeholder'] = force_text(attrs.get('placeholder'))

        return format_html(
            DATETIMEPICKER_WIDGET_STRING,
            id=force_text(final_attrs['id']),
            name=force_text(final_attrs['name']),
            placeholder=force_text(final_attrs['placeholder']),
            value=final_attrs['value']
        )


class TimePickerInput(TextInput):
    """
    This form widget metaclass mixin activates Bootstrap Datetimepicker
    """

    def __init__(self, attrs=None):
        super(TimePickerInput, self).__init__(attrs)
        self.input_type = 'text'

    def render(self, name, value, attrs=None):
        """
        Renders this widget
        :param name: Name attribute of the input type
        :param value: Value, if any
        :param attrs: Dictionary of additional attributes and their values
        :return: HTML
        """

        if value is None:
            value = ''

        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            final_attrs['value'] = format_html('value="{}"', force_text(self._format_value(value)))
        else:
            final_attrs['value'] = ''

        # Kept for backwards compatibility with existing forms.
        final_attrs['placeholder'] = 'Den skal vises fra ...'
        if attrs.get('placeholder', False):
            # Update the placeholder text if supplied.
            final_attrs['placeholder'] = force_text(attrs.get('placeholder'))

        return format_html(
            DATETIMEPICKER_WIDGET_STRING,
            id=force_text(final_attrs['id']),
            name=force_text(final_attrs['name']),
            placeholder=force_text(final_attrs['placeholder']),
            value=final_attrs['value']
        )
