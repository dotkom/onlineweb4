# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_auto_20150420_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrelation',
            name='payment_price',
            field=models.ForeignKey(default=0, to='payment.PaymentPrice'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paymentprice',
            name='payment',
            field=models.ForeignKey(to='payment.Payment'),
            preserve_default=True,
        ),
    ]
