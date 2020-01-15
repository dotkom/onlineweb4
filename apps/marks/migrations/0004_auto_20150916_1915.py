# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("marks", "0003_suspension")]

    operations = [
        migrations.AddField(
            model_name="suspension",
            name="title",
            field=models.CharField(default="", max_length=64, verbose_name="tittel"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="suspension",
            name="active",
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
