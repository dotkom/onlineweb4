# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import User
from django.db import models

class RegisterToken(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField("token", max_length=32)
    created = models.DateTimeField("created", editable=False, auto_now_add=True, default=datetime.datetime.now())

    @property
    def is_valid(self):
        valid_period = datetime.timedelta(days=1)
        now = datetime.datetime.now()
        return now < self.created + valid_period 
