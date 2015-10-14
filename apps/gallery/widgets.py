# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/14/15

from django.forms import HiddenInput
from django.forms.utils import flatatt, format_html, force_text


class SingleImageField(HiddenInput):
    """
    SingleImageField adds wrapper HTML around the hidden input field containing the ResponsiveImage ID
    """

    def __init__(self, attrs=None):
        super(SingleImageField, self).__init__(attrs)
        self.input_type = 'hidden'

    def render(self, name, value, attrs=None):
        """
        Renders this field widget as HTML
        :param name: Field input name
        :param value: Field input value
        :param attrs: Field input attributes
        :return: An HTML string representing this widget
        """

        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the value attribute if the value is non-empty
            final_attrs['value'] = force_text(self._format_value(value))

        widget_string = """<br /><input{} />\r\n
<a href="#" class="btn btn-primary" id="add-responsive-image">\r\n
<i class="fa fa-plus fa-lg"></i> Velg</a>\r\n
<a href="#" class="btn btn-primary" id="upload-responsive-image">\r\n
<i class="fa fa-image fa-lg"></i> Last opp</a>\r\n"""

        return format_html(widget_string, flatatt(final_attrs))
