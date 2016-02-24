# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_auto_20160128_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onlineuser',
            name='field_of_study',
            field=models.SmallIntegerField(default=0, verbose_name='studieretning', choices=[(0, 'Gjest'), (1, 'Bachelor i Informatikk'), (10, 'Programvaresystemer'), (11, 'Databaser og s\xf8k'), (12, 'Algoritmer og datamaskiner'), (13, 'Spillteknologi'), (14, 'Kunstig intelligens'), (15, 'Helseinformatikk'), (30, 'Annen mastergrad'), (80, 'PhD'), (90, 'International'), (100, 'Annet Onlinemedlem')]),
        ),
    ]
