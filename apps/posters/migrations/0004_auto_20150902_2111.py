# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0003_auto_20150826_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poster',
            name='display_from',
            field=models.DateField(null=True, verbose_name='vis fra', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='poster',
            name='display_to',
            field=models.DateField(null=True, verbose_name='vis til', blank=True),
            preserve_default=True,
        ),
    ]
