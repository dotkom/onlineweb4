# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webshop', '0006_auto_20151104_2009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='images',
        ),
        migrations.AddField(
            model_name='product',
            name='images_csv',
            field=models.CommaSeparatedIntegerField(default=None, max_length=200, blank=True, null=True),
        ),
    ]
