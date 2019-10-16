# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0005_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='multiplechoicequestion',
            options={'verbose_name': 'Flervalgsp\xf8rsm\xe5l', 'verbose_name_plural': 'Flervalgsp\xf8rsm\xe5l', 'permissions': (('view_multiplechoicequestion', 'View MultipleChoiceQuestion'),)},
        ),
    ]
