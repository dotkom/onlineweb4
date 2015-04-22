# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_auto_20150420_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='stripe_key_index',
            field=models.SmallIntegerField(default=0, verbose_name='stripe key', choices=[(0, b'Arrkom'), (1, b'Prokom')]),
            preserve_default=False,
        ),
    ]
