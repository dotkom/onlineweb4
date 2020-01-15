# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("marks", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="mark",
            name="category",
            field=models.SmallIntegerField(
                default=0,
                verbose_name="kategori",
                choices=[
                    (0, "Ingen"),
                    (1, "Sosialt"),
                    (2, "Bedriftspresentasjon"),
                    (3, "Kurs"),
                    (4, "Tilbakemelding"),
                    (5, "Kontoret"),
                    (6, "Betaling"),
                ],
            ),
            preserve_default=True,
        )
    ]
