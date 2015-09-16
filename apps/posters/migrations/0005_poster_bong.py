# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0004_auto_20150902_2111'),
    ]

    operations = [
        migrations.AddField(
            model_name='poster',
            name='bong',
            field=models.IntegerField(null=True, verbose_name='bonger', blank=True),
            preserve_default=True,
        ),
    ]
