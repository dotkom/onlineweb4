# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("splash", "0005_auto_20150422_2236")]

    operations = [
        migrations.AlterField(
            model_name="splashevent",
            name="created",
            field=django_extensions.db.fields.CreationDateTimeField(
                auto_now_add=True, verbose_name="created"
            ),
        ),
        migrations.AlterField(
            model_name="splashevent",
            name="modified",
            field=django_extensions.db.fields.ModificationDateTimeField(
                auto_now=True, verbose_name="modified"
            ),
        ),
    ]
