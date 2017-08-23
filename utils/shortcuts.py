# -*- coding: utf8 -*-
import json

from django.http import HttpResponse

from utils.helpers import JsonHelper


def render_json(data=None, error=None, status=200):
    """
    Returns a HTTPResponse with the data represented as json.
    Takes data or error as argument. data can be objects, lists
    or dictionaries. The JsonHelper class defines how different
    objects are serialized to json.

    If error is set the view will have status code 400. That helps
    when using jquery success and error callbacks.
    """
    if data is None:
        if status == 200:
            status = 400

        if error is None:
            error = 'Too few arguments to render json'

        data = {
            'error': error
        }

    return HttpResponse(
        json.dumps(data, cls=JsonHelper),
        content_type="application/json",
        status=status
    )
