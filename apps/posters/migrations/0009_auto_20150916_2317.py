# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0008_auto_20150916_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermixin',
            name='display_from',
            field=models.DateField(default=None, null=True, verbose_name='vis fra', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='poster',
            name='display_to',
            field=models.DateField(default=None, null=True, verbose_name='vis til', blank=True),
            preserve_default=True,
        ),
    ]
