# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_auto_20150416_0200'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.IntegerField(verbose_name='pris')),
                ('description', models.CharField(max_length=128, null=True, blank=True)),
                ('payment', models.ForeignKey(related_name='prices', to='payment.Payment')),
            ],
            options={
                'verbose_name': 'pris',
                'verbose_name_plural': 'priser',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='payment',
            name='price',
        ),
    ]
