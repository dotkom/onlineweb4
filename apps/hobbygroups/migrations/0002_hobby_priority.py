# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-08-08 18:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("hobbygroups", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="hobby", name="priority", field=models.IntegerField(default=0)
        )
    ]
