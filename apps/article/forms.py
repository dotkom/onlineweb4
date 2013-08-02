from django.forms.models import modelform_factory
from django.db.models.loading import get_models, get_app, get_apps
from django import forms
from widgets import PopUpBaseWidget

class UploadForm(forms.Form):
    name = forms.CharField(widget=PopUpBaseWidget)

def normalize_model_name(model_name):
    if (model_name.lower() == model_name):
        normal_model_name = model.name.capitalize()
    else:
        normal_model_name = model_name

    return normal_model_name

def get_model_form(model_name):
    app_list = get_apps()
    for app in app_list:
        for model in get_models(app):
            if model.__name__ == model.name:
                form = modelform_factory(model)
                return form
    raise Exception('Did not find the model %s' % (model_name))
