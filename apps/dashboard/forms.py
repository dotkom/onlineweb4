from django.contrib.admin.widgets import AdminFileWidget
from django.forms import Form
from django.forms.widgets import FileInput, HiddenInput


class HTML5RequiredMixin(Form):
    """
    Uses Django widget to set the `required` property on HTML fields in HTML forms.
    http://stackoverflow.com/a/30210382
    """

    def __init__(self, *args, **kwargs):
        super(HTML5RequiredMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            if (self.fields[field].required and
               type(self.fields[field].widget) not in
                    (AdminFileWidget, HiddenInput, FileInput) and
               '__prefix__' not in self.fields[field].widget.attrs):

                self.fields[field].widget.attrs['required'] = 'required'
                if self.fields[field].label:
                    self.fields[field].label += ' *'
