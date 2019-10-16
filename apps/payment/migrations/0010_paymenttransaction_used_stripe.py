# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_auto_20151021_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenttransaction',
            name='used_stripe',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
