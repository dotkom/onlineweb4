# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0003_auto_20150304_2206'),
    ]

    operations = [
        migrations.AddField(
            model_name='poster',
            name='done',
            field=models.BooleanField(default=False, verbose_name='ferdig'),
            preserve_default=True,
        ),
    ]
