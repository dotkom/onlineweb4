# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_grouprestriction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouprestriction',
            name='id',
        ),
        migrations.AlterField(
            model_name='grouprestriction',
            name='event',
            field=models.OneToOneField(related_name='group_restriction', primary_key=True, serialize=False, to='events.Event'),
            preserve_default=True,
        ),
    ]
