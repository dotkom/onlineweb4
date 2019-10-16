# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0014_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlineuser',
            name='saldo',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='saldo'),
        ),
    ]
