# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("article", "0002_auto_20150218_2217")]

    operations = [
        migrations.RenameField(
            model_name="article", old_name="image", new_name="old_image"
        )
    ]
