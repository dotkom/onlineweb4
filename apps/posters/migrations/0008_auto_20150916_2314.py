# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0007_auto_20150916_2246'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poster',
            name='display_from',
        ),
        migrations.AddField(
            model_name='ordermixin',
            name='display_from',
            field=models.DateField(null=True, verbose_name='vis fra', blank=True),
            preserve_default=True,
        ),
    ]
