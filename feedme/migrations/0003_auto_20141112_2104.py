# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedme', '0002_auto_20141026_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='use_validation',
            field=models.BooleanField(default=True, verbose_name='Enable funds validation'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderline',
            name='price',
            field=models.IntegerField(max_length=4, verbose_name='price'),
            preserve_default=True,
        ),
    ]
