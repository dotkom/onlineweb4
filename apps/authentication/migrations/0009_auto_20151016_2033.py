# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authentication", "0008_auto_20151014_2156")]

    operations = [
        migrations.AlterField(
            model_name="onlineuser",
            name="bio",
            field=models.TextField(default="", verbose_name="bio", blank=True),
            preserve_default=False,
        )
    ]
