# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0010_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='deadline',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
