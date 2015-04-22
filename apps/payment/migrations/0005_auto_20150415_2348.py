# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20150415_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrelation',
            name='stripe_id',
            field=models.CharField(default=0, max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='delay',
            field=models.SmallIntegerField(default=2, null=True, verbose_name='utsettelse', blank=True),
            preserve_default=True,
        ),
    ]
