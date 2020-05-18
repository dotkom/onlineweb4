# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payment", "0006_auto_20151014_1938"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("amount", models.IntegerField(null=True, blank=True)),
                ("datetime", models.DateTimeField(auto_now=True)),
                (
                    "item",
                    models.ForeignKey(
                        blank=True,
                        to="inventory.Item",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "verbose_name": "transaksjon",
                "verbose_name_plural": "transaksjoner",
            },
            bases=(models.Model,),
        )
    ]
