# -*- coding: utf-8 -*-


import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authentication", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="onlineuser",
            name="started_date",
            field=models.DateField(
                default=django.utils.timezone.now, verbose_name="startet studie"
            ),
            preserve_default=True,
        )
    ]
