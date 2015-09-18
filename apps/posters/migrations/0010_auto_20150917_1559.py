# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0009_auto_20150916_2317'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordermixin',
            options={'permissions': (('add_poster_order', 'Add poster orders'), ('overview_poster_order', 'View poster order overview'), ('view_poster_order', 'View poster orders'))},
        ),
    ]
