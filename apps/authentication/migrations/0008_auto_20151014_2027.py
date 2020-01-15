# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authentication", "0007_auto_20151014_2010")]

    operations = [
        migrations.AlterField(
            model_name="position",
            name="position",
            field=models.CharField(
                default=b"medlem",
                max_length=10,
                verbose_name="stilling",
                choices=[
                    (b"medlem", "Medlem"),
                    (b"leder", "Leder"),
                    (b"nestleder", "Nestleder"),
                    (b"okoans", "\xd8konomiansvarlig"),
                    (b"redaktor", "Redakt\xf8r"),
                ],
            ),
            preserve_default=True,
        )
    ]
