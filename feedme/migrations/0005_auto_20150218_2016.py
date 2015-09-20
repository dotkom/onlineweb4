# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedme', '0004_auto_20150203_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='menu_item',
            field=models.CharField(max_length=50, verbose_name='menu item'),
            preserve_default=True,
        ),
    ]
