# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0004_poster_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='poster',
            name='finished',
            field=models.BooleanField(default=False, verbose_name='ferdig'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='poster',
            name='category',
            field=models.IntegerField(default=0, verbose_name='type', choices=[(0, 'Plakat'), (1, 'Banner'), (2, 'Bong')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='poster',
            name='location',
            field=models.CharField(max_length=50, verbose_name='sted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='poster',
            name='title',
            field=models.CharField(max_length=50, verbose_name='arrangementstittel'),
            preserve_default=True,
        ),
    ]
