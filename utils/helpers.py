# -*- coding: utf8 -*-
from datetime import datetime, date
import json

from django.db.models.query import QuerySet
from django.db import models


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