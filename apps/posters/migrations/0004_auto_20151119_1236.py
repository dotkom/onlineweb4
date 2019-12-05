# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("posters", "0003_ordermixin_comment")]

    operations = [
        migrations.AlterField(
            model_name="ordermixin",
            name="comments",
            field=models.TextField(null=True, verbose_name="kommentar", blank=True),
        )
    ]
