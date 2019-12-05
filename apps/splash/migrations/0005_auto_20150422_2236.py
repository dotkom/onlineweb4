# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("splash", "0004_auto_20150422_2234")]

    operations = [
        migrations.AlterModelOptions(
            name="splashevent", options={"ordering": ("start_time",)}
        )
    ]
