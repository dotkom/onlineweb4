# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poster',
            name='amount',
            field=models.IntegerField(null=True, verbose_name='antall', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='poster',
            name='price',
            field=models.DecimalField(null=True, verbose_name='pris', max_digits=10, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='poster',
            name='comments',
            field=models.TextField(max_length=500, null=True, verbose_name='kommentar', blank=True),
            preserve_default=True,
        ),
    ]
