# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermixin',
            name='order_type',
            field=models.TextField(default=b'plakat', max_length=20, verbose_name='type'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ordermixin',
            name='amount',
            field=models.IntegerField(null=True, verbose_name='antall opplag', blank=True),
            preserve_default=True,
        ),
    ]
