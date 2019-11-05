# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Batch",
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
                ("amount", models.IntegerField(default=0, verbose_name="Antall")),
                (
                    "date_added",
                    models.DateField(auto_now_add=True, verbose_name="Dato lagt til"),
                ),
                (
                    "expiration_date",
                    models.DateField(
                        null=True, verbose_name="Utl\xf8psdato", blank=True
                    ),
                ),
            ],
            options={"verbose_name": "Batch", "verbose_name_plural": "Batches"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Item",
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
                ("name", models.CharField(max_length=50, verbose_name="Varetype")),
            ],
            options={
                "verbose_name": "Vare",
                "verbose_name_plural": "Varer",
                "permissions": (("view_item", "View Inventory Item"),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="batch",
            name="item",
            field=models.ForeignKey(
                related_name="batches",
                verbose_name="Vare",
                to="inventory.Item",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
