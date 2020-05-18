# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("article", "0009_article_tags")]

    operations = [
        migrations.AlterUniqueTogether(name="articletag", unique_together=set([])),
        migrations.RemoveField(model_name="articletag", name="article"),
        migrations.RemoveField(model_name="articletag", name="tag"),
        migrations.RemoveField(model_name="article", name="old_image"),
        migrations.RemoveField(model_name="article", name="photographers"),
        migrations.DeleteModel(name="ArticleTag"),
        migrations.DeleteModel(name="Tag"),
    ]
