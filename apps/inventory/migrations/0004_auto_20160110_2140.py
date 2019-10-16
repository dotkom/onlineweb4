# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_item_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='avalible',
            new_name='available',
        ),
    ]
