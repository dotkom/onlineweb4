# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0006_auto_20151104_2228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productsize',
            name='stock',
        ),
        migrations.AddField(
            model_name='productrelation',
            name='stock',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
