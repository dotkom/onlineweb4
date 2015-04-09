# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0008_auto_20150409_0654'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poster',
            options={'ordering': ['-id'], 'verbose_name': 'plakatbestilling', 'verbose_name_plural': 'plakatbestillinger', 'permissions': (('add_poster_order', 'Add poster orders'), ('overview_poster_order', 'View poster order overview'), ('view_poster_order', 'View poster orders'))},
        ),
    ]
