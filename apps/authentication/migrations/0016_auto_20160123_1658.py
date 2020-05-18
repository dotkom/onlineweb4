# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authentication", "0015_auto_20160123_1633")]

    operations = [
        migrations.AlterField(
            model_name="onlineuser",
            name="saldo",
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name="saldo",
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        )
    ]
