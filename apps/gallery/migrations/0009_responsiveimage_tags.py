# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0002_auto_20150616_2121"),
        ("gallery", "0008_auto_20151024_1845"),
    ]

    operations = [
        migrations.AddField(
            model_name="responsiveimage",
            name="tags",
            field=taggit.managers.TaggableManager(
                to="taggit.Tag",
                through="taggit.TaggedItem",
                help_text="A comma-separated list of tags.",
                verbose_name="Tags",
            ),
        )
    ]
