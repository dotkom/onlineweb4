from django.db import models
from django import forms

class VimeoVideoField(models.CharField):
    description = "VimeoVideoField"
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 200
        super(VimeoVideoField, self).__init__(*args, **kwargs)
