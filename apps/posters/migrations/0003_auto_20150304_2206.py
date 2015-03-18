# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0002_auto_20150304_2154'),
    ]

    operations = [
        migrations.RenameField(
            model_name='poster',
            old_name='ordered_by_group',
            new_name='ordered_committee',
        ),
    ]
