# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0006_auto_20151024_2111'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='additional_authors',
            new_name='authors',
        ),
    ]
