# -*- coding: utf8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.forms import HiddenInput, TextInput
from django.forms.utils import flatatt, force_text, format_html

from apps.gallery.models import ResponsiveImage
from apps.gallery.widgets import SingleImageInput


WIDGET_STRING = """<br /><input{} />\r\n
<div id="multiple-images-field-thumbnail">{}</div>
<a href="#" class="btn btn-primary" id="add-responsive-images">\r\n
<i class="fa fa-plus fa-lg"></i> Velg bilder</a>\r\n
<a href="{}" class="btn btn-primary" target="_blank">\r\n
<i class="fa fa-image fa-lg"></i> Last opp</a>\r\n
<a href="#" class="btn btn-danger" id="dashboard-gallery-remove-images">\r\n
<i class="fa fa-times fa-lg"></i> Fjern bilder</a><br>\r\n
<div id="image-selection-wrapper">\r\n
<h2 id="image-selection-title">Velg bilde</h2>\r\n
<div class="row">\r\n
<div class="col-md-12">\r\n
<div class="input-group">\r\n
<input type="text" id="image-gallery-search" class="form-control" placeholder="Skriv inn søkeord...">\r\n
<span class="input-group-btn">\r\n
<a class="btn btn-primary" id="image-gallery-search-button" type="button">Søk!</a>\r\n
</span>\r\n
</div>\r\n
</div>\r\n
</div>\r\n
<hr />\r\n
<div class="row multiple" id="image-gallery-search-results"></div>\r\n
</div>\r\n"""



class MultipleImagesInput(HiddenInput):
  def __init__(self, attrs=None):
        super(MultipleImagesInput, self).__init__(attrs)
        self.input_type = 'hidden'

  def render(self, name, value, attrs={'mulitple: True'}):
      """
      Renders this field widget as HTML
      :param name: Field input name
      :param value: Field input value
      :param attrs: Field input attributes
      :return: An HTML string representing this widget
      """

      print("Value: ", value)
      is_empty = not value
      #value = value[0]
      #if value is None or []:
      #    value = ''



      img_thumb = 'Det er ikke valgt noen bilder.'

      attrs = self.build_attrs(self.attrs, attrs)
      final_attrs = self.build_attrs(attrs, {'type': self.input_type, 'name': name})
      
      if value:
          #values = value.split(',')
          value = value.split(',')[0]
          # Only add the value attribute if the value is non-empty
          final_attrs['value'] = force_text(self._format_value(value))
          img = ResponsiveImage.objects.get(pk=value)
          img_thumb = format_html(
              '<img class="multiple" src="{}" alt title="{}"/>',
              settings.MEDIA_URL + str(img.thumbnail),
              str(img.name),
              encoding='utf-8'

          )
      upload_url = reverse_lazy('gallery_dashboard:upload')

      #return format_html(WIDGET_STRING, flatatt(final_attrs), img_thumb, upload_url)  
      return ResponsiveImage.objects.get(pk=1)

