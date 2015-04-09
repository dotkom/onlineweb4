# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0006_auto_20150408_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poster',
            name='amount',
            field=models.IntegerField(null=True, verbose_name='antall plakater', blank=True),
            preserve_default=True,
        ),
    ]
