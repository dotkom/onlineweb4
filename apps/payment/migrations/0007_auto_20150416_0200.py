# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_payment_refunded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='refunded',
        ),
        migrations.AddField(
            model_name='paymentrelation',
            name='refunded',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
