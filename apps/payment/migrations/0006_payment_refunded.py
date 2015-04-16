# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20150415_2348'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='refunded',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
