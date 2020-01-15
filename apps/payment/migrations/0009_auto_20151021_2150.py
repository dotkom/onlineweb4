# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("payment", "0008_auto_20151017_2047")]

    operations = [
        migrations.RemoveField(model_name="itemrelation", name="item"),
        migrations.RemoveField(model_name="itemrelation", name="transaction"),
        migrations.DeleteModel(name="ItemRelation"),
    ]
