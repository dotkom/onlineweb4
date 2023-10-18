# -*- coding: utf8 -*-
import json
from datetime import date, datetime

from django.db import models
from django.db.models.query import QuerySet


class JsonHelper(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%d.%m.%Y %H.%M")

        elif isinstance(obj, date):
            return obj.strftime("%d.%m.%Y")

        elif isinstance(obj, models.Model):
            return obj.serializable_object()

        elif isinstance(obj, QuerySet):
            return list(obj)

        return json.JSONEncoder.default(self, obj)


def humanize_size(size, suffix="B"):
    """
    Converts an integer of bytes to a properly scaled human readable
    string.

    Example:
    >>> humanize_size(15298253)
    '14.6MB'

    :param size: The size of the object in bytes as an integer
    :return: A string of the formatted file size
    """

    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(size) < 1024.0:
            return "%.1f%s%s" % (size, unit, suffix)
        size /= 1024.0
    return "%.1f%s%s" % (size, "", suffix)
