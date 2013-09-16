from django import forms
from django.template.loader import render_to_string

class PopUpBaseWidget(object):
    def __init__(self, model=None, template="addnew.html", *args, **kwargs):
        self.model = model
        self.template = template
        super(PopUpBaseWidget, self).__init__(*args, **kwargs)

        def render(self, name, *args, **kwargs):
            html = super(PopUpBaseWidget, self).render(name, *args, **kwargs)

            if not self.model:
                self.model = name
            
            popupplus = render_to_string(self.template, {'field':name, 'model':self.model})
            return html + popupplus
