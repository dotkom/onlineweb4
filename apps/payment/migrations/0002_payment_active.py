# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("payment", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="active",
            field=models.BooleanField(default=False),
            preserve_default=True,
        )
    ]
