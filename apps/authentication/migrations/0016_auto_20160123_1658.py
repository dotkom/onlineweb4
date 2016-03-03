# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0015_auto_20160123_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlineuser',
            name='saldo',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='saldo', validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
