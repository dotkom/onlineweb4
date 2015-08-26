# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('splash', '0003_auto_20150422_2218'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='splashevent',
            options={'ordering': ('-start_time',)},
        ),
    ]
