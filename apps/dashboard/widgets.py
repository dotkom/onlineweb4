# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/18/15

from django.forms.widgets import TextInput
from django.forms.utils import force_text, format_html

DATETIMEPICKER_WIDGET_STRING = """
<div class="input-group dtp">\r\n
<span class="input-group-btn datepickerbutton">\r\n
<a href="#" class="btn btn-primary">\r\n
<i class="fa fa-calendar fa-lg"></i></a></span>\r\n
<input class="form-control" id="{}" name="{}" type="text" {} placeholder="Artikkel skal vises fra ..." />\r\n
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
        final_attrs['value'] = force_text(self._format_value(value))

        return format_html(
            DATETIMEPICKER_WIDGET_STRING,
            force_text(final_attrs['id']),
            force_text(final_attrs['name']),
            final_attrs['value']
        )
