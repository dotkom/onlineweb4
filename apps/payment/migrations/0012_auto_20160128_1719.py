# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("payment", "0011_merge")]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="stripe_key_index",
            field=models.SmallIntegerField(
                verbose_name="stripe key",
                choices=[(0, b"Arrkom"), (1, b"Prokom"), (2, b"Trikom")],
            ),
        )
    ]
