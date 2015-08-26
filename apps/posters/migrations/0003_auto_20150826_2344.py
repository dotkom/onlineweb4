# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0002_auto_20150429_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermixin',
            name='order_type',
            field=models.IntegerField(choices=[(1, b'Plakat'), (2, b'Bong'), (3, b'Annet')]),
            preserve_default=True,
        ),
    ]
