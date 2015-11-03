# -*- coding: utf8 -*-
#
# Created by 'myth' on 10/14/15

from django.conf import settings
from django.forms import HiddenInput, TextInput
from django.forms.utils import flatatt, format_html, force_text

from apps.gallery.models import ResponsiveImage

WIDGET_STRING = """<br /><input{} />\r\n
<div id="single-image-field-thumbnail">{}</div>
<a href="#" class="btn btn-primary" id="add-responsive-image">\r\n
<i class="fa fa-plus fa-lg"></i> Velg</a>\r\n
<a href="#" class="btn btn-primary" id="upload-responsive-image">\r\n
<i class="fa fa-image fa-lg"></i> Last opp</a><br>\r\n
<div id="image-selection-wrapper">\r\n
<h2 id="image-selection-title">Velg bilde</h2>\r\n
<div class="row">\r\n
<div class="col-md-12">\r\n
<div class="input-group">\r\n
<input type="text" id="image-gallery-search" class="form-control" placeholder="Skriv inn søkeord...">\r\n
<span class="input-group-btn">\r\n
<button class="btn btn-primary" id="image-gallery-search-button" type="button">Søk!</button>\r\n
</span>\r\n
</div>\r\n
</div>\r\n
</div>\r\n
<hr />\r\n
<div class="row" id="image-gallery-search-results"></div>\r\n
</div>\r\n"""


class SingleImageInput(HiddenInput):
    """
    SingleImageField adds wrapper HTML around the hidden input field containing the ResponsiveImage ID
    """

    def __init__(self, attrs=None):
        super(SingleImageInput, self).__init__(attrs)
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

        img_thumb = 'Det er ikke valgt noe bilde.'
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the value attribute if the value is non-empty
            final_attrs['value'] = force_text(self._format_value(value))
            img = ResponsiveImage.objects.get(pk=value)
            img_thumb = format_html(
                '<img src="{}" alt title="{}"/>',
                settings.MEDIA_URL + str(img.thumbnail),
                str(img.name),
                encoding='utf-8'
            )

        return format_html(WIDGET_STRING, flatatt(final_attrs), img_thumb)


class TagInputField(TextInput):
    """
    Adds some extras to a TextInputField to support space or comma separated tagging
    """

    def __init__(self, attrs=None):
        super(TagInputField, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        return super(TagInputField, self).render(name, value, attrs=attrs)
