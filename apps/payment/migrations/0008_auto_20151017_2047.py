# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0002_auto_20151016_2157"),
        ("payment", "0007_paymenttransaction"),
    ]

    operations = [
        migrations.CreateModel(
            name="ItemRelation",
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
                (
                    "item",
                    models.ForeignKey(to="inventory.Item", on_delete=models.CASCADE),
                ),
                (
                    "transaction",
                    models.ForeignKey(
                        to="payment.PaymentTransaction", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name="paymenttransaction",
            options={
                "ordering": ["-datetime"],
                "verbose_name": "transaksjon",
                "verbose_name_plural": "transaksjoner",
            },
        ),
        migrations.RemoveField(model_name="paymenttransaction", name="item"),
    ]
