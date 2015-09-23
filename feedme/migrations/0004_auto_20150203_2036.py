# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedme', '0003_auto_20141112_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='poll',
            field=models.ForeignKey(related_name='votes', to='feedme.Poll'),
            preserve_default=True,
        ),
    ]
