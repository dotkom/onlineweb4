# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0003_auto_20151118_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='datetime',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
