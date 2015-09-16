# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0006_auto_20150916_1935'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='generalorder',
            options={'ordering': ['-id'], 'verbose_name': 'generell bestilling', 'verbose_name_plural': 'generelle bestillinger'},
        ),
        migrations.AlterModelOptions(
            name='poster',
            options={'ordering': ['-id'], 'verbose_name': 'plakatbestilling', 'verbose_name_plural': 'plakatbestillinger'},
        ),
    ]
