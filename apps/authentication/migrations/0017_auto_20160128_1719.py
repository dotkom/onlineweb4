# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0016_auto_20160123_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlineuser',
            name='saldo',
            field=models.PositiveSmallIntegerField(default=0, null=True, verbose_name='saldo'),
        ),
    ]
